"""REST uçlarının birim testleri — altyapısız, sahte sağlayıcılarla.

Gerçek Redis/PG davranışı entegrasyon testlerinde; burada uçların sözleşmesi
(plan Bölüm 9: yollar, alan adları, durum kodları) sabitlenir.
"""

from datetime import UTC, datetime

from httpx import ASGITransport, AsyncClient

from app.adapters.cikan.redis_durum import AracAnlik, CihazAnlik
from app.adapters.giren.rest.bagimliliklar import (
    anlik_durumu_getir,
    esikleri_getir,
    sorgulari_getir,
)
from app.application.olcum_isle import SeviyeEsikleri
from app.domain.modeller import Cihaz, Hat, Olcum
from app.main import uygulama_olustur

SIMDI = datetime(2026, 7, 8, 14, 35, 12, tzinfo=UTC)


class SahteAnlikDurum:
    """Redis okuma yüzeyinin sahtesi."""

    def __init__(
        self,
        hat_doluluklari: dict[int, dict[int, float]] | None = None,
        arac_durumlari: dict[int, AracAnlik] | None = None,
        cihaz_durumlari: dict[str, CihazAnlik] | None = None,
    ) -> None:
        self._hat_doluluklari = hat_doluluklari or {}
        self._arac_durumlari = arac_durumlari or {}
        self._cihaz_durumlari = cihaz_durumlari or {}

    async def hat_arac_doluluklari(self, hat_id: int) -> dict[int, float]:
        return self._hat_doluluklari.get(hat_id, {})

    async def hat_ozeti(self, hat_id: int) -> tuple[float | None, int]:
        doluluklar = self._hat_doluluklari.get(hat_id, {})
        if not doluluklar:
            return None, 0
        return sum(doluluklar.values()) / len(doluluklar), len(doluluklar)

    async def arac_durumu(self, arac_id: int) -> AracAnlik | None:
        return self._arac_durumlari.get(arac_id)

    async def cihaz_durumu(self, cihaz_id: str) -> CihazAnlik | None:
        return self._cihaz_durumlari.get(cihaz_id)


class SahteSorgular:
    """PostgreSQL okuma yüzeyinin sahtesi."""

    def __init__(
        self,
        hatlar: list[Hat] = (),
        cihazlar: list[Cihaz] = (),
        trend: list[dict] = (),
        olcumler: list[Olcum] = (),
    ) -> None:
        self.hatlar = list(hatlar)
        self.cihazlar = list(cihazlar)
        self._trend = list(trend)
        self._olcumler = list(olcumler)

    async def hatlari_listele(self) -> list[Hat]:
        return self.hatlar

    async def cihazlari_listele(self) -> list[Cihaz]:
        return self.cihazlar

    async def hat_trendi(
        self, hat_id: int, baslangic: datetime, bitis: datetime, aralik: str
    ) -> list[dict]:
        return self._trend

    async def arac_olcumleri(
        self, arac_id: int, baslangic: datetime, bitis: datetime
    ) -> list[Olcum]:
        return self._olcumler


def _istemci(anlik: SahteAnlikDurum, sorgular: SahteSorgular) -> AsyncClient:
    uygulama = uygulama_olustur()
    uygulama.dependency_overrides[anlik_durumu_getir] = lambda: anlik
    uygulama.dependency_overrides[sorgulari_getir] = lambda: sorgular
    # Eşikler sabit: test, geliştirici ortamının .env'inden etkilenmez (hermetik).
    uygulama.dependency_overrides[esikleri_getir] = lambda: SeviyeEsikleri(
        seyrek_ust=0.40, orta_ust=0.70
    )
    return AsyncClient(transport=ASGITransport(app=uygulama), base_url="http://test")


async def test_hatlar_listesi_ortalama_ve_seviye_icerir() -> None:
    anlik = SahteAnlikDurum(hat_doluluklari={1: {10: 0.9, 11: 0.66}})
    sorgular = SahteSorgular(hatlar=[Hat(id=1, hat_no="34", ad="Zincirlikuyu – Söğütlüçeşme")])

    async with _istemci(anlik, sorgular) as istemci:
        yanit = await istemci.get("/api/hatlar")

    assert yanit.status_code == 200
    (hat,) = yanit.json()
    assert hat["hat_id"] == 1
    assert hat["hat_no"] == "34"
    assert hat["arac_sayisi"] == 2
    assert abs(hat["ortalama_doluluk"] - 0.78) < 1e-9
    assert hat["seviye"] == "yogun"


async def test_verisi_olmayan_hat_bos_ortalama_doner() -> None:
    anlik = SahteAnlikDurum()
    sorgular = SahteSorgular(hatlar=[Hat(id=2, hat_no="42", ad="Kadıköy – Ümraniye")])

    async with _istemci(anlik, sorgular) as istemci:
        yanit = await istemci.get("/api/hatlar")

    (hat,) = yanit.json()
    assert hat["ortalama_doluluk"] is None
    assert hat["seviye"] is None
    assert hat["arac_sayisi"] == 0


async def test_hat_anlik_arac_durumlarini_doner() -> None:
    anlik = SahteAnlikDurum(
        hat_doluluklari={1: {10: 0.5}},
        arac_durumlari={
            10: AracAnlik(kisi_sayisi=45, doluluk_orani=0.5, seviye="orta", zaman=SIMDI)
        },
    )

    async with _istemci(anlik, SahteSorgular()) as istemci:
        yanit = await istemci.get("/api/hatlar/1/anlik")

    assert yanit.status_code == 200
    (arac,) = yanit.json()
    assert arac["arac_id"] == 10
    assert arac["kisi_sayisi"] == 45
    assert arac["doluluk_orani"] == 0.5
    assert arac["seviye"] == "orta"


async def test_trend_sorgusu_zaman_serisi_doner() -> None:
    nokta = {
        "zaman": SIMDI,
        "ortalama_doluluk": 0.42,
        "ortalama_kisi": 38.0,
        "olcum_sayisi": 12,
    }
    sorgular = SahteSorgular(trend=[nokta])

    async with _istemci(SahteAnlikDurum(), sorgular) as istemci:
        yanit = await istemci.get(
            "/api/hatlar/1/trend",
            params={
                "baslangic": "2026-07-08T00:00:00Z",
                "bitis": "2026-07-08T23:59:59Z",
                "aralik": "saat",
            },
        )

    assert yanit.status_code == 200
    (satir,) = yanit.json()
    assert satir["ortalama_doluluk"] == 0.42
    assert satir["olcum_sayisi"] == 12


async def test_trend_gecersiz_aralik_422_doner() -> None:
    async with _istemci(SahteAnlikDurum(), SahteSorgular()) as istemci:
        yanit = await istemci.get(
            "/api/hatlar/1/trend",
            params={
                "baslangic": "2026-07-08T00:00:00Z",
                "bitis": "2026-07-08T23:59:59Z",
                "aralik": "gun",
            },
        )

    assert yanit.status_code == 422


async def test_arac_olcumleri_doner() -> None:
    olcum = Olcum(
        cihaz_id="edge_0001",
        sira_no=7,
        kisi_sayisi=23,
        olcum_zamani=SIMDI,
        arac_id=10,
        hat_id=1,
        doluluk_orani=0.256,
        seviye="seyrek",
    )
    sorgular = SahteSorgular(olcumler=[olcum])

    async with _istemci(SahteAnlikDurum(), sorgular) as istemci:
        yanit = await istemci.get(
            "/api/araclar/10/olcumler",
            params={"baslangic": "2026-07-08T00:00:00Z", "bitis": "2026-07-08T23:59:59Z"},
        )

    assert yanit.status_code == 200
    (satir,) = yanit.json()
    assert satir["sira_no"] == 7
    assert satir["kisi_sayisi"] == 23
    assert satir["seviye"] == "seyrek"


async def test_cihazlar_cevrimici_durumuyla_listelenir() -> None:
    sorgular = SahteSorgular(
        cihazlar=[
            Cihaz(id="edge_0001", tip="arac", yazilim_surumu="1.0.0"),
            Cihaz(id="edge_0006", tip="durak", yazilim_surumu="1.0.0"),
        ]
    )
    anlik = SahteAnlikDurum(
        cihaz_durumlari={
            "edge_0001": CihazAnlik(cevrimici=True, son_gorulme=SIMDI, yazilim_surumu="1.2.0")
        }
    )

    async with _istemci(anlik, sorgular) as istemci:
        yanit = await istemci.get("/api/cihazlar")

    assert yanit.status_code == 200
    cihazlar = {c["id"]: c for c in yanit.json()}
    assert cihazlar["edge_0001"]["cevrimici"] is True
    assert cihazlar["edge_0001"]["son_gorulme"] is not None
    assert cihazlar["edge_0006"]["cevrimici"] is False  # hiç durum yazılmamış
    assert cihazlar["edge_0006"]["son_gorulme"] is None
