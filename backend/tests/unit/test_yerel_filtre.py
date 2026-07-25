"""Yerel üretici ön-filtresi birim testleri.

Gerçek veride 168 satır / ~25 bin karakter özet çıkıyor; yerel model bu boyutta
talimatı kaybedip düz metne kaçıyor (canlı doğrulandı). Bulut modelinde şema
API'de zorlandığı için sorun yok, bu yüzden filtre yalnız yerel yolda uygulanır:
zaten prompt "yalnız belirgin sapma gösteren örüntüler" istiyor.
"""

from app.adapters.cikan._yerel_filtre import belirgin_sapmalar

AZAMI = 12


def _satir(hat_id: int, doluluk: float, karsilastirma: float | None) -> dict:
    return {
        "hat_id": hat_id,
        "gun_no": 1,
        "saat_baslangic": 8,
        "ortalama_doluluk": doluluk,
        "karsilastirma_ortalama_doluluk": karsilastirma,
    }


def test_belirgin_sapma_secilir():
    satirlar = [_satir(1, 0.90, 0.40)]  # +0.50 sapma

    assert belirgin_sapmalar(satirlar, azami=AZAMI) == satirlar


def test_sapmasiz_satir_elenir():
    satirlar = [_satir(1, 0.42, 0.40)]  # +0.02, gürültü

    assert belirgin_sapmalar(satirlar, azami=AZAMI) == []


def test_karsilastirmasi_olmayan_satir_elenir():
    # Karşılaştırma yoksa "diğer günlere göre sapma" iddiası kurulamaz.
    satirlar = [_satir(1, 0.95, None)]

    assert belirgin_sapmalar(satirlar, azami=AZAMI) == []


def test_en_buyuk_sapmalar_oncelikli_ve_azami_uygulanir():
    satirlar = [
        _satir(1, 0.70, 0.40),  # +0.30
        _satir(2, 0.95, 0.40),  # +0.55  (en büyük)
        _satir(3, 0.85, 0.40),  # +0.45
    ]

    sonuc = belirgin_sapmalar(satirlar, azami=2)

    assert [s["hat_id"] for s in sonuc] == [2, 3]


def test_bos_girdi_bos_doner():
    assert belirgin_sapmalar([], azami=AZAMI) == []


def test_negatif_sapma_da_belirgindir():
    # Beklenenden çok düşük doluluk da operasyonel olarak anlamlıdır.
    satirlar = [_satir(1, 0.10, 0.60)]  # -0.50

    assert belirgin_sapmalar(satirlar, azami=AZAMI) == satirlar
