"""UyariUret use-case birim testleri — SAHTE (in-memory) adaptörlerle."""

from datetime import UTC, datetime

from app.application.olcum_isle import SeviyeEsikleri
from app.application.uyari_uret import UyariUret
from app.domain.modeller import Uyari

ESIKLER = SeviyeEsikleri(seyrek_ust=0.40, orta_ust=0.70)

OZET_SEYREK = {"hat_id": 1, "ortalama_doluluk": 0.20, "ortalama_kisi": 15.0, "olcum_sayisi": 10}
OZET_YOGUN = {"hat_id": 2, "ortalama_doluluk": 0.85, "ortalama_kisi": 76.0, "olcum_sayisi": 12}

UYARI = Uyari(
    hat_id=2,
    ortalama_doluluk=0.85,
    ortalama_kisi=76.0,
    uyari_metni="2 numaralı hat şu anda yoğun, ek sefer değerlendirilebilir.",
    gerekce="Son 3 saatte ortalama doluluk %85.",
    olusturulma_zamani=datetime(2026, 7, 13, tzinfo=UTC),
)


class SahteAnlikOzetSorgusu:
    def __init__(self, ozet: list[dict] = ()) -> None:
        self._ozet = list(ozet)

    async def hat_anlik_ozet(
        self, baslangic: datetime, bitis: datetime, min_olcum_sayisi: int = 3
    ) -> list[dict]:
        return self._ozet


class SahteUyariUreticisi:
    def __init__(self, uyarilar: list[Uyari] = ()) -> None:
        self._uyarilar = list(uyarilar)
        self.cagri_sayisi = 0
        self.son_ozet_veri: list[dict] | None = None

    async def uret(self, ozet_veri: list[dict]) -> list[Uyari]:
        self.cagri_sayisi += 1
        self.son_ozet_veri = ozet_veri
        return self._uyarilar


class SahteUyariDeposu:
    def __init__(self) -> None:
        self.kaydedilenler: list[Uyari] = []

    async def ekle(self, uyarilar: list[Uyari]) -> None:
        self.kaydedilenler.extend(uyarilar)

    async def son_uyarilar(self, limit: int = 50) -> list[Uyari]:
        return self.kaydedilenler[:limit]


async def test_bos_ozet_veri_llm_cagrilmaz() -> None:
    sorgular = SahteAnlikOzetSorgusu([])
    uretici = SahteUyariUreticisi([UYARI])
    depo = SahteUyariDeposu()
    use_case = UyariUret(
        sorgular=sorgular, uyari_uretici=uretici, uyari_deposu=depo, esikler=ESIKLER
    )

    sonuc = await use_case.calistir()

    assert sonuc == []
    assert uretici.cagri_sayisi == 0
    assert depo.kaydedilenler == []


async def test_tum_hatlar_esik_altinda_llm_cagrilmaz() -> None:
    sorgular = SahteAnlikOzetSorgusu([OZET_SEYREK])
    uretici = SahteUyariUreticisi([UYARI])
    depo = SahteUyariDeposu()
    use_case = UyariUret(
        sorgular=sorgular, uyari_uretici=uretici, uyari_deposu=depo, esikler=ESIKLER
    )

    sonuc = await use_case.calistir()

    assert sonuc == []
    assert uretici.cagri_sayisi == 0
    assert depo.kaydedilenler == []


async def test_yogun_hat_sadece_o_satir_llme_gider_ve_depoya_yazilir() -> None:
    sorgular = SahteAnlikOzetSorgusu([OZET_SEYREK, OZET_YOGUN])
    uretici = SahteUyariUreticisi([UYARI])
    depo = SahteUyariDeposu()
    use_case = UyariUret(
        sorgular=sorgular, uyari_uretici=uretici, uyari_deposu=depo, esikler=ESIKLER
    )

    sonuc = await use_case.calistir()

    assert sonuc == [UYARI]
    assert depo.kaydedilenler == [UYARI]
    assert uretici.son_ozet_veri == [OZET_YOGUN]


async def test_llm_bos_liste_donerse_depoya_yazma_atlanir() -> None:
    sorgular = SahteAnlikOzetSorgusu([OZET_YOGUN])
    uretici = SahteUyariUreticisi([])
    depo = SahteUyariDeposu()
    use_case = UyariUret(
        sorgular=sorgular, uyari_uretici=uretici, uyari_deposu=depo, esikler=ESIKLER
    )

    sonuc = await use_case.calistir()

    assert sonuc == []
    assert depo.kaydedilenler == []
