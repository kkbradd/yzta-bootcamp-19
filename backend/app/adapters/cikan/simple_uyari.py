"""Yerel uyarı üretici — OpenJarvis SimpleAgent + Ollama, veri makineden çıkmaz.

Gemini üreticisiyle aynı `UyariUreticiPort` sözleşmesi ve aynı prompt/şema/eşleme
(_uyari_ortak); yerel LLM çağrısı ve JSON zorlaması _yerel_llm'de ortaktır.
"""

from typing import Any

from app.adapters.cikan._llm_ayristir import dogrula_veya_bos
from app.adapters.cikan._uyari_ortak import (
    SISTEM_PROMPT,
    UyariListesi,
    maddeleri_uyarilara_cevir,
)
from app.adapters.cikan._yerel_llm import json_talimati, yerel_calistir
from app.domain.modeller import Uyari

_SEMA = '{"uyarilar": [{"hat_id": int, "uyari_metni": str, "gerekce": str}]}.'


class SimpleUyariUreticisi:
    """UyariUreticiPort implementasyonu — yerel SimpleAgent ile."""

    def __init__(self, motor: Any, model: str) -> None:
        self._motor = motor
        self._model = model

    async def uret(self, ozet_veri: list[dict]) -> list[Uyari]:
        if not ozet_veri:
            return []
        ham = yerel_calistir(
            self._motor, self._model, SISTEM_PROMPT + json_talimati(_SEMA), ozet_veri
        )
        veri = dogrula_veya_bos(ham, UyariListesi, "uyarilar")
        return maddeleri_uyarilara_cevir(veri.uyarilar, ozet_veri)
