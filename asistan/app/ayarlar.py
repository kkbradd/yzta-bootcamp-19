"""Asistan servisi ayarları — tümü ortam değişkenlerinden okunur."""

import os
from dataclasses import dataclass

ISTEK_ZAMAN_ASIMI_SN = 10.0
AZAMI_TUR = 6
AZAMI_TOKEN = 512
SICAKLIK = 0.0
VARSAYILAN_TREND_SAATI = 3


@dataclass(frozen=True, slots=True)
class Ayarlar:
    yotay_api_adresi: str
    ollama_adresi: str
    model: str
    motor: str

    @classmethod
    def ortamdan(cls) -> "Ayarlar":
        return cls(
            yotay_api_adresi=os.getenv("YOTAY_API_ADRESI", "http://localhost:8000"),
            ollama_adresi=os.getenv("OLLAMA_ADRESI", "http://localhost:11434"),
            model=os.getenv("ASISTAN_MODEL", "qwen3.5:0.8b"),
            motor=os.getenv("ASISTAN_MOTOR", "ollama"),
        )
