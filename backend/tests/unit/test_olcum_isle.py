"""OlcumIsleyici use-case birim testleri — SAHTE (in-memory) adaptörlerle.

PostgreSQL/Redis/broker gerektirmez (kabul kriteri #9). Hattın sözleşmesi
(plan Bölüm 8): dedup → zenginleştir (çekim damgasına göre atama çözümü +
denormalizasyon) → seviye hesapla → depoya yaz → anlık durumu güncelle → yayınla.
"""

from datetime import UTC, datetime

from app.application.olcum_isle import OlcumIsleyici, SeviyeEsikleri
from app.domain.modeller import Arac, CihazAtamasi, HatAtamasi, Olcum
from app.domain.seviye import SEVIYE_YOGUN

T0 = datetime(2026, 7, 1, tzinfo=UTC)
T1 = datetime(2026, 7, 5, tzinfo=UTC)
SIMDI = datetime(2026, 7, 8, 14, 35, 12, tzinfo=UTC)


class SahteOlcumDeposu:
    def __init__(self) -> None:
        self.kayitlar: list[Olcum] = []
        self._anahtarlar: set[tuple[str, int]] = set()

    async def ekle(self, olcum: Olcum) -> bool:
        anahtar = (olcum.cihaz_id, olcum.sira_no)
        if anahtar in self._anahtarlar:
            return False
        self._anahtarlar.add(anahtar)
        self.kayitlar.append(olcum)
        return True


class SahteAtamaDeposu:
    def __init__(
        self,
        cihaz_atamalari: list[CihazAtamasi] = (),
        hat_atamalari: list[HatAtamasi] = (),
        araclar: dict[int, Arac] | None = None,
    ) -> None:
        self.cihaz_atamalari = list(cihaz_atamalari)
        self.hat_atamalari = list(hat_atamalari)
        self.araclar = araclar or {}

    async def cihaz_atamasini_bul(self, cihaz_id: str, an: datetime) -> CihazAtamasi | None:
        return next(
            (
                a
                for a in self.cihaz_atamalari
                if a.cihaz_id == cihaz_id and _aralikta(a.baslangic, a.bitis, an)
            ),
            None,
        )

    async def hat_atamasini_bul(self, arac_id: int, an: datetime) -> HatAtamasi | None:
        return next(
            (
                a
                for a in self.hat_atamalari
                if a.arac_id == arac_id and _aralikta(a.baslangic, a.bitis, an)
            ),
            None,
        )

    async def arac_getir(self, arac_id: int) -> Arac | None:
        return self.araclar.get(arac_id)


def _aralikta(baslangic: datetime, bitis: datetime | None, an: datetime) -> bool:
    return baslangic <= an and (bitis is None or bitis > an)


class SahteAnlikDurum:
    def __init__(self) -> None:
        self.arac_yazimlari: list[Olcum] = []
        self.cihaz_yazimlari: list[tuple] = []

    async def arac_durumunu_yaz(self, olcum: Olcum) -> None:
        self.arac_yazimlari.append(olcum)

    async def cihaz_durumunu_yaz(
        self, cihaz_id: str, cevrimici: bool, yazilim_surumu: str | None, son_gorulme: datetime
    ) -> None:
        self.cihaz_yazimlari.append((cihaz_id, cevrimici, yazilim_surumu, son_gorulme))


class SahteYayin:
    def __init__(self) -> None:
        self.arac_guncellemeleri: list[Olcum] = []
        self.cihaz_durumlari: list[tuple] = []

    async def arac_guncellemesini_yayinla(self, olcum: Olcum) -> None:
        self.arac_guncellemeleri.append(olcum)

    async def cihaz_durumunu_yayinla(
        self, cihaz_id: str, cevrimici: bool, son_gorulme: datetime
    ) -> None:
        self.cihaz_durumlari.append((cihaz_id, cevrimici, son_gorulme))


def _isleyici_kur(
    atama_deposu: SahteAtamaDeposu,
) -> tuple[OlcumIsleyici, SahteOlcumDeposu, SahteAnlikDurum, SahteYayin]:
    depo = SahteOlcumDeposu()
    anlik = SahteAnlikDurum()
    yayin = SahteYayin()
    isleyici = OlcumIsleyici(
        olcum_deposu=depo,
        atama_deposu=atama_deposu,
        anlik_durum=anlik,
        canli_yayin=yayin,
        esikler=SeviyeEsikleri(seyrek_ust=0.40, orta_ust=0.70),
    )
    return isleyici, depo, anlik, yayin


def _arac_atamalari() -> SahteAtamaDeposu:
    """edge_0042 → araç 7 (kapasite 30) → hat 3; güncel atamalar."""
    return SahteAtamaDeposu(
        cihaz_atamalari=[CihazAtamasi(id=1, cihaz_id="edge_0042", baslangic=T0, arac_id=7)],
        hat_atamalari=[HatAtamasi(id=1, hat_id=3, arac_id=7, baslangic=T0)],
        araclar={7: Arac(id=7, plaka="34 HAT 007", tip="midibus", kapasite=30)},
    )


async def test_arac_olcumu_zenginlesir_yazilir_ve_yayinlanir() -> None:
    isleyici, depo, anlik, yayin = _isleyici_kur(_arac_atamalari())

    olcum = await isleyici.isle(
        cihaz_id="edge_0042", sira_no=18452, kisi_sayisi=23, olcum_zamani=SIMDI
    )

    assert olcum is not None
    assert olcum.arac_id == 7
    assert olcum.hat_id == 3
    assert olcum.doluluk_orani is not None and abs(olcum.doluluk_orani - 23 / 30) < 1e-9
    assert olcum.seviye == SEVIYE_YOGUN
    assert depo.kayitlar == [olcum]
    assert anlik.arac_yazimlari == [olcum]
    assert yayin.arac_guncellemeleri == [olcum]


async def test_mukerrer_sira_no_ikinci_kez_islenmez() -> None:
    # MQTT QoS 1 aynı mesajı iki kez getirebilir; ikincisi hiçbir yan etki üretmemeli.
    isleyici, depo, anlik, yayin = _isleyici_kur(_arac_atamalari())

    ilk = await isleyici.isle("edge_0042", 18452, 23, SIMDI)
    ikinci = await isleyici.isle("edge_0042", 18452, 23, SIMDI)

    assert ilk is not None and ikinci is None
    assert len(depo.kayitlar) == 1
    assert len(anlik.arac_yazimlari) == 1
    assert len(yayin.arac_guncellemeleri) == 1


async def test_kayitsiz_cihaz_sistemi_dusurmez_hicbir_sey_yazilmaz() -> None:
    isleyici, depo, anlik, yayin = _isleyici_kur(SahteAtamaDeposu())

    olcum = await isleyici.isle("edge_9999", 1, 5, SIMDI)

    assert olcum is None
    assert depo.kayitlar == []
    assert anlik.arac_yazimlari == []
    assert yayin.arac_guncellemeleri == []


async def test_durak_cihazinda_yalniz_sayi_saklanir() -> None:
    # Durakta kapasite yok → oran ve seviye None; anlık araç durumu ve yayın tetiklenmez.
    atamalar = SahteAtamaDeposu(
        cihaz_atamalari=[CihazAtamasi(id=1, cihaz_id="edge_0006", baslangic=T0, durak_id=1)]
    )
    isleyici, depo, anlik, yayin = _isleyici_kur(atamalar)

    olcum = await isleyici.isle("edge_0006", 5, 12, SIMDI)

    assert olcum is not None
    assert olcum.arac_id is None and olcum.hat_id is None
    assert olcum.doluluk_orani is None and olcum.seviye is None
    assert depo.kayitlar == [olcum]
    assert anlik.arac_yazimlari == []
    assert yayin.arac_guncellemeleri == []


async def test_gecikmeli_mesaj_cekim_anindaki_atamaya_islenir() -> None:
    # Tünel modu: cihaz T0-T1 arasında araç 7'deydi, T1'de araç 8'e taşındı.
    # Çekim damgası T0-T1 aralığında → ölçüm araç 7'ye (ve onun hattına) yazılmalı.
    atamalar = SahteAtamaDeposu(
        cihaz_atamalari=[
            CihazAtamasi(id=1, cihaz_id="edge_0042", baslangic=T0, bitis=T1, arac_id=7),
            CihazAtamasi(id=2, cihaz_id="edge_0042", baslangic=T1, arac_id=8),
        ],
        hat_atamalari=[
            HatAtamasi(id=1, hat_id=3, arac_id=7, baslangic=T0),
            HatAtamasi(id=2, hat_id=5, arac_id=8, baslangic=T0),
        ],
        araclar={
            7: Arac(id=7, plaka="34 HAT 007", tip="midibus", kapasite=30),
            8: Arac(id=8, plaka="34 HAT 008", tip="otobus", kapasite=60),
        },
    )
    isleyici, _, _, _ = _isleyici_kur(atamalar)
    gecmis_damga = datetime(2026, 7, 3, tzinfo=UTC)  # T0 < damga < T1

    olcum = await isleyici.isle("edge_0042", 100, 15, gecmis_damga)

    assert olcum is not None
    assert olcum.arac_id == 7  # o anki değil, çekim anındaki araç
    assert olcum.hat_id == 3
