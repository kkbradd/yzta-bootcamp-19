"""Hava durumu + yoğun saat bilgisinden doluluk tahmini yapan OpenJarvis aracı.

Model ekip arkadaşlarının eğittiği scikit-learn pipeline'ıdır (joblib artefaktı).

DİKKAT — bu bir DEMO modelidir: artefaktın kendi uyarısına göre gerçek bus.csv
verisinde hava/saat ile doluluk arasında ilişki bulunamamış (R²~0), model
kural-tabanlı sentetik veriyle eğitilmiştir. Tool çıktısı bu yüzden her zaman
tahmin olduğunu belirten bir not taşır; asistanın kesin ölçüm gibi sunmasını
önler. Gerçek veriyle yeniden eğitilirse `_TAHMIN_NOTU` gözden geçirilmeli.
"""

import logging
from pathlib import Path
from typing import Any

from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec

logger = logging.getLogger("asistan.yogunluk_tahmini")

VARSAYILAN_MODEL_YOLU = Path(__file__).resolve().parent.parent / "model" / (
    "bus_congestion_model_DEMO.joblib"
)

# Model İngilizce etiketlerle eğitildi; kullanıcı Türkçe sorduğu için eşlenir.
HAVA_KARSILIKLARI = {
    "açık": "Clear",
    "acik": "Clear",
    "güneşli": "Clear",
    "gunesli": "Clear",
    "bulutlu": "Cloudy",
    "kapalı": "Cloudy",
    "kapali": "Cloudy",
    "sisli": "Fog",
    "sis": "Fog",
    "yağmurlu": "Rain",
    "yagmurli": "Rain",
    "yagmurlu": "Rain",
    "yağmur": "Rain",
    "yagmur": "Rain",
    "karlı": "Snow",
    "karli": "Snow",
    "kar": "Snow",
    "fırtına": "Storm",
    "firtina": "Storm",
    "fırtınalı": "Storm",
    "firtinali": "Storm",
}

_TAHMIN_NOTU = (
    "Not: Bu bir tahmindir (sentetik veriyle eğitilmiş demo modeli), "
    "gerçek ölçüm değildir."
)


class ModelYuklenemedi(RuntimeError):
    """joblib artefaktı okunamadı — sebebi mesajda."""


class YogunlukTahminModeli:
    """joblib artefaktını sarar; tahmini yüzde olarak döner."""

    def __init__(self, artefakt: dict[str, Any]) -> None:
        self._pipeline = artefakt["pipeline"]
        self._gecerli_havalar = list(artefakt["valid_weather_conditions"])
        self._surum = artefakt.get("model_version", "bilinmiyor")

    @classmethod
    def yoldan(cls, yol: Path = VARSAYILAN_MODEL_YOLU) -> "YogunlukTahminModeli":
        import joblib

        if not yol.is_file():
            raise ModelYuklenemedi(
                f"Tahmin modeli bulunamadı: '{yol}'. "
                "asistan/model/ altına joblib artefaktını koyun."
            )
        try:
            return cls(joblib.load(yol))
        except (KeyError, ValueError, EOFError) as hata:
            raise ModelYuklenemedi(f"Tahmin modeli okunamadı: {hata}") from hata

    @property
    def gecerli_havalar(self) -> list[str]:
        return list(self._gecerli_havalar)

    @property
    def surum(self) -> str:
        return self._surum

    def tahmin_et(self, hava_durumu: str, saat_yogun_mu: bool) -> float:
        """Yüzde doluluk tahmini (0-100 aralığına kırpılır)."""
        import pandas as pd

        girdi = pd.DataFrame(
            [{"weather_condition": hava_durumu, "peak_hour": 1 if saat_yogun_mu else 0}]
        )
        ham = float(self._pipeline.predict(girdi)[0])
        return round(max(0.0, min(100.0, ham)), 1)


def hava_durumunu_cevir(ham: str) -> str | None:
    """Türkçe/İngilizce hava girdisini modelin beklediği etikete çevirir."""
    temiz = ham.strip().lower()
    if temiz in HAVA_KARSILIKLARI:
        return HAVA_KARSILIKLARI[temiz]
    for gecerli in ("Clear", "Cloudy", "Fog", "Rain", "Snow", "Storm"):
        if temiz == gecerli.lower():
            return gecerli
    return None


class YogunlukTahminiAraci(BaseTool):
    """Hava ve saat bilgisinden beklenen doluluğu tahmin eder."""

    tool_id = "yogunluk_tahmini"

    def __init__(self, model: YogunlukTahminModeli) -> None:
        self._model = model

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="yogunluk_tahmini",
            description=(
                "Hava durumuna ve saatin yoğun olup olmadığına göre otobüs doluluk "
                "yüzdesini TAHMİN eder. Gelecek/varsayımsal sorularda kullanılır "
                "(örn. 'yağmur yağarsa ne kadar dolu olur')."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "hava_durumu": {
                        "type": "string",
                        "description": "Hava: açık, bulutlu, sisli, yağmurlu, karlı, fırtınalı",
                    },
                    "yogun_saat": {
                        "type": "boolean",
                        "description": "Yoğun saat mi (sabah/akşam zirvesi) — true/false",
                    },
                },
                "required": ["hava_durumu"],
            },
            category="yotay",
        )

    def execute(self, **params: Any) -> ToolResult:
        try:
            return ToolResult(tool_name=self.spec.name, content=self._calistir(**params))
        except ModelYuklenemedi as hata:
            logger.warning("tahmin modeli kullanılamadı: %s", hata)
            return ToolResult(tool_name=self.spec.name, content=str(hata), success=False)

    def _calistir(self, hava_durumu: str, yogun_saat: Any = False) -> str:
        etiket = hava_durumunu_cevir(str(hava_durumu))
        if etiket is None:
            secenekler = ", ".join(self._model.gecerli_havalar)
            return (
                f"'{hava_durumu}' hava durumu tanınmadı. "
                f"Geçerli değerler: {secenekler} (veya açık/bulutlu/sisli/yağmurlu/karlı/fırtınalı)."
            )

        yogun_mu = _mantiksal_oku(yogun_saat)
        yuzde = self._model.tahmin_et(etiket, yogun_mu)
        saat_metni = "yoğun saatte" if yogun_mu else "sakin saatte"
        return f"{etiket} havada {saat_metni} beklenen doluluk: %{yuzde}. {_TAHMIN_NOTU}"


def _mantiksal_oku(deger: Any) -> bool:
    """Model 'true'/'evet' gibi metin de üretebildiği için esnek okunur."""
    if isinstance(deger, bool):
        return deger
    return str(deger).strip().lower() in ("true", "1", "evet", "yes", "var")
