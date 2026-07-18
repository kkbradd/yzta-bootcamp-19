"""Ortak öneri/uyarı eşleme birim testleri — Gemini ve yerel üretici bunu paylaşır.

LLM'in uydurduğu (özet veride olmayan) hat/gün/saat kombinasyonları atılmalı;
gerçek değerler (doluluk, kişi sayısı) LLM'den değil özet veriden alınmalı.
"""

from app.adapters.cikan._oneri_ortak import OneriMaddesi, maddeleri_onerilere_cevir
from app.adapters.cikan._uyari_ortak import UyariMaddesi, maddeleri_uyarilara_cevir

OZET_ONERI = [
    {"hat_id": 1, "gun_no": 1, "saat_baslangic": 8, "ortalama_doluluk": 0.9,
     "karsilastirma_ortalama_doluluk": 0.4},
]
OZET_UYARI = [{"hat_id": 1, "ortalama_doluluk": 0.85, "ortalama_kisi": 70.0}]


def _oneri_maddesi(hat_id: int = 1, gun_no: int = 1, saat: int = 8) -> OneriMaddesi:
    return OneriMaddesi(
        hat_id=hat_id, gun_no=gun_no, saat_baslangic=saat, saat_bitis=saat + 2,
        oneri_metni="metin", gerekce="gerekce",
    )


def test_eslesen_madde_oneriye_cevrilir():
    sonuc = maddeleri_onerilere_cevir([_oneri_maddesi()], OZET_ONERI)

    assert len(sonuc) == 1
    assert sonuc[0].hat_id == 1


def test_saat_bitis_yoksa_baslangictan_turetilir():
    """Model saat_bitis'i atlarsa yanıt düşmemeli; sorgu saatlik gruplar (+1)."""
    madde = OneriMaddesi(
        hat_id=1, gun_no=1, saat_baslangic=8, oneri_metni="metin", gerekce="gerekce"
    )

    sonuc = maddeleri_onerilere_cevir([madde], OZET_ONERI)

    assert len(sonuc) == 1
    assert sonuc[0].saat_bitis == 9


def test_gercek_doluluk_ozetten_alinir_llmden_degil():
    sonuc = maddeleri_onerilere_cevir([_oneri_maddesi()], OZET_ONERI)

    assert sonuc[0].ortalama_doluluk == 0.9
    assert sonuc[0].karsilastirma_ortalama_doluluk == 0.4


def test_uydurma_hat_atlanir():
    sonuc = maddeleri_onerilere_cevir([_oneri_maddesi(hat_id=99)], OZET_ONERI)

    assert sonuc == []


def test_uydurma_gun_atlanir():
    sonuc = maddeleri_onerilere_cevir([_oneri_maddesi(gun_no=5)], OZET_ONERI)

    assert sonuc == []


def test_uyari_maddesi_cevrilir_ve_kisi_sayisi_ozetten_gelir():
    madde = UyariMaddesi(hat_id=1, uyari_metni="metin", gerekce="gerekce")

    sonuc = maddeleri_uyarilara_cevir([madde], OZET_UYARI)

    assert len(sonuc) == 1
    assert sonuc[0].ortalama_kisi == 70.0


def test_uyari_uydurma_hat_atlanir():
    madde = UyariMaddesi(hat_id=42, uyari_metni="metin", gerekce="gerekce")

    sonuc = maddeleri_uyarilara_cevir([madde], OZET_UYARI)

    assert sonuc == []
