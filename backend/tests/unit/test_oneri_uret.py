"""OneriUret use-case birim testleri — SAHTE (in-memory) adaptörlerle."""

from datetime import UTC, datetime

from app.application.oneri_uret import OneriUret
from app.domain.modeller import Oneri

OZET_SATIR = {
    "hat_id": 1,
    "gun_no": 1,
    "saat_baslangic": 8,
    "ortalama_doluluk": 0.88,
    "ortalama_kisi": 79.0,
    "olcum_sayisi": 20,
}

ONERI = Oneri(
    hat_id=1,
    gun_no=1,
    saat_baslangic=8,
    saat_bitis=10,
    ortalama_doluluk=0.88,
    karsilastirma_ortalama_doluluk=0.42,
    oneri_metni="Pazartesi 08-10 arası sefer sıklığını artırmayı düşünün.",
    gerekce="Diğer günlere göre belirgin sapma var.",
    olusturulma_zamani=datetime(2026, 7, 13, tzinfo=UTC),
)


class SahteHaftalikOruntuSorgusu:
    def __init__(self, ozet: list[dict] = ()) -> None:
        self._ozet = list(ozet)

    async def hat_haftalik_oruntu(
        self, baslangic: datetime, bitis: datetime, min_olcum_sayisi: int = 5
    ) -> list[dict]:
        return self._ozet


class SahteOneriUreticisi:
    def __init__(self, oneriler: list[Oneri] = ()) -> None:
        self._oneriler = list(oneriler)
        self.cagri_sayisi = 0

    async def uret(self, ozet_veri: list[dict]) -> list[Oneri]:
        self.cagri_sayisi += 1
        return self._oneriler


class SahteOneriDeposu:
    def __init__(self) -> None:
        self.kaydedilenler: list[Oneri] = []

    async def ekle(self, oneriler: list[Oneri]) -> None:
        self.kaydedilenler.extend(oneriler)

    async def son_oneriler(self, limit: int = 50) -> list[Oneri]:
        return self.kaydedilenler[:limit]


async def test_bos_ozet_veri_llm_cagrilmaz() -> None:
    sorgular = SahteHaftalikOruntuSorgusu([])
    uretici = SahteOneriUreticisi([ONERI])
    depo = SahteOneriDeposu()
    use_case = OneriUret(sorgular=sorgular, oneri_uretici=uretici, oneri_deposu=depo)

    sonuc = await use_case.calistir()

    assert sonuc == []
    assert uretici.cagri_sayisi == 0
    assert depo.kaydedilenler == []


async def test_dolu_ozet_veri_depoya_yazilir() -> None:
    sorgular = SahteHaftalikOruntuSorgusu([OZET_SATIR])
    uretici = SahteOneriUreticisi([ONERI])
    depo = SahteOneriDeposu()
    use_case = OneriUret(sorgular=sorgular, oneri_uretici=uretici, oneri_deposu=depo)

    sonuc = await use_case.calistir()

    assert sonuc == [ONERI]
    assert depo.kaydedilenler == [ONERI]


async def test_llm_bos_liste_donerse_depoya_yazma_atlanir() -> None:
    sorgular = SahteHaftalikOruntuSorgusu([OZET_SATIR])
    uretici = SahteOneriUreticisi([])
    depo = SahteOneriDeposu()
    use_case = OneriUret(sorgular=sorgular, oneri_uretici=uretici, oneri_deposu=depo)

    sonuc = await use_case.calistir()

    assert sonuc == []
    assert depo.kaydedilenler == []
