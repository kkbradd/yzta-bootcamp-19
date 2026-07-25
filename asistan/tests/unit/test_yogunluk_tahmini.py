"""Yoğunluk tahmin aracı: hava çevirisi, tahmin metni ve hata akışları."""

from pathlib import Path

import pytest

from app.yogunluk_tahmini import (
    ModelYuklenemedi,
    YogunlukTahminiAraci,
    YogunlukTahminModeli,
    hava_durumunu_cevir,
)


class SahtePipeline:
    """predict çağrısını kaydeder; sabit yüzde döner."""

    def __init__(self, sonuc: float = 62.5) -> None:
        self.sonuc = sonuc
        self.son_girdi: dict | None = None

    def predict(self, girdi):
        self.son_girdi = girdi.iloc[0].to_dict()
        return [self.sonuc]


def _model(sonuc: float = 62.5) -> tuple[YogunlukTahminModeli, SahtePipeline]:
    pipeline = SahtePipeline(sonuc)
    artefakt = {
        "pipeline": pipeline,
        "valid_weather_conditions": ["Clear", "Cloudy", "Fog", "Rain", "Snow", "Storm"],
        "model_version": "test_1.0",
    }
    return YogunlukTahminModeli(artefakt), pipeline


@pytest.mark.parametrize(
    ("girdi", "beklenen"),
    [
        ("yağmurlu", "Rain"),
        ("YAĞMUR", "Rain"),
        ("karlı", "Snow"),
        ("açık", "Clear"),
        ("fırtınalı", "Storm"),
        ("sisli", "Fog"),
        ("bulutlu", "Cloudy"),
        ("Rain", "Rain"),
        ("storm", "Storm"),
    ],
)
def test_hava_durumu_turkce_ve_ingilizce_cevrilir(girdi, beklenen):
    assert hava_durumunu_cevir(girdi) == beklenen


def test_taninmayan_hava_none_doner():
    assert hava_durumunu_cevir("kavurucu") is None


def test_tahmin_yuzde_ve_uyari_icerir():
    model, _ = _model(sonuc=62.5)
    arac = YogunlukTahminiAraci(model)

    sonuc = arac.execute(hava_durumu="yağmurlu", yogun_saat=True)

    assert sonuc.success
    assert "%62.5" in sonuc.content
    assert "yoğun saatte" in sonuc.content
    # Sentetik model uyarısı çıktıdan düşerse asistan tahmini ölçüm gibi sunar.
    assert "tahmindir" in sonuc.content


def test_taninmayan_hava_aciklayici_mesaj_doner():
    model, _ = _model()
    arac = YogunlukTahminiAraci(model)

    sonuc = arac.execute(hava_durumu="kavurucu")

    assert sonuc.success  # kullanıcı hatası, API arızası değil
    assert "tanınmadı" in sonuc.content
    assert "Clear" in sonuc.content


def test_yogun_saat_modele_iletilir():
    model, pipeline = _model()
    arac = YogunlukTahminiAraci(model)

    arac.execute(hava_durumu="açık", yogun_saat=True)

    assert pipeline.son_girdi == {"weather_condition": "Clear", "peak_hour": 1}


def test_yogun_saat_metin_olarak_da_okunur():
    """Küçük model boolean yerine 'true' metni üretebiliyor."""
    model, pipeline = _model()
    arac = YogunlukTahminiAraci(model)

    arac.execute(hava_durumu="açık", yogun_saat="true")

    assert pipeline.son_girdi["peak_hour"] == 1


def test_yogun_saat_varsayilani_sakin():
    model, pipeline = _model()
    arac = YogunlukTahminiAraci(model)

    arac.execute(hava_durumu="açık")

    assert pipeline.son_girdi["peak_hour"] == 0
    assert "sakin saatte" in arac.execute(hava_durumu="açık").content


@pytest.mark.parametrize(("ham", "beklenen"), [(-15.0, 0.0), (140.0, 100.0)])
def test_tahmin_yuzde_araligina_kirpilir(ham, beklenen):
    model, _ = _model(sonuc=ham)
    assert model.tahmin_et("Clear", False) == beklenen


def test_model_dosyasi_yoksa_acik_hata():
    with pytest.raises(ModelYuklenemedi, match="bulunamadı"):
        YogunlukTahminModeli.yoldan(Path("/olmayan/model.joblib"))
