"""Asistan servisi ayarları — tümü ortam değişkenlerinden okunur."""

import os
from dataclasses import dataclass

ISTEK_ZAMAN_ASIMI_SN = 10.0
AZAMI_TUR = 6
AZAMI_TOKEN = 512
SICAKLIK = 0.0
VARSAYILAN_TREND_SAATI = 3

GEMINI_ANAHTAR_DEGISKENLERI = ("GEMINI_API_KEY", "GOOGLE_API_KEY")
BULUT_MOTORU = "cloud"


class AyarHatasi(ValueError):
    """Ayarlar tutarsız — servis açılmadan önce fark edilir."""


def _gemini_anahtarini_oku() -> str:
    for degisken in GEMINI_ANAHTAR_DEGISKENLERI:
        anahtar = os.getenv(degisken, "")
        if anahtar:
            return anahtar
    return ""


@dataclass(frozen=True, slots=True)
class Ayarlar:
    yotay_api_adresi: str
    ollama_adresi: str
    model: str
    motor: str
    gemini_anahtari: str = ""

    @property
    def gemini_mi(self) -> bool:
        """OpenJarvis sağlayıcıyı model adından seçer (bkz. `_is_google_model`)."""
        return "gemini" in self.model.lower()

    @property
    def bulut_mu(self) -> bool:
        return self.motor == BULUT_MOTORU

    @classmethod
    def ortamdan(cls) -> "Ayarlar":
        ayarlar = cls(
            yotay_api_adresi=os.getenv("YOTAY_API_ADRESI", "http://localhost:8000"),
            ollama_adresi=os.getenv("OLLAMA_ADRESI", "http://localhost:11434"),
            model=os.getenv("ASISTAN_MODEL", "qwen3.5:0.8b"),
            motor=os.getenv("ASISTAN_MOTOR", "ollama"),
            gemini_anahtari=_gemini_anahtarini_oku(),
        )
        ayarlar._dogrula()
        return ayarlar

    def _dogrula(self) -> None:
        # OpenJarvis tutarsızlığı sessizce yutar: kimlik bilgisi/motor uyuşmazsa
        # CloudEngine.health() False döner, get_engine lokale düşer ve kullanıcı
        # Gemini beklerken qwen'den (ya da hiç çekilmemiş modelden) cevap alır.
        # Motor ve model tek bir kararı kodladığı için ikisi de tutarlı olmalı.
        if self.bulut_mu and not self.gemini_mi:
            raise AyarHatasi(
                f"ASISTAN_MOTOR={BULUT_MOTORU} yalnız Gemini modelleriyle desteklenir; "
                f"{self.model} verildi. Gemini için ASISTAN_MODEL=gemini-3-flash kullanın."
            )
        if self.gemini_mi and not self.bulut_mu:
            raise AyarHatasi(
                f"{self.model} bulut modeli, ASISTAN_MOTOR={self.motor} ile çalışmaz. "
                f"ASISTAN_MOTOR={BULUT_MOTORU} verin."
            )
        if self.gemini_mi and not self.gemini_anahtari:
            raise AyarHatasi(
                f"{self.model} modeli için GEMINI_API_KEY (veya GOOGLE_API_KEY) gerekli. "
                "Lokal çalışmak için ASISTAN_MODEL ve ASISTAN_MOTOR'u ayarlamayın."
            )
