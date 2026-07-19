"""Yerel öneri üretici — OpenJarvis SimpleAgent + Ollama, veri makineden çıkmaz.

Gemini üreticisiyle aynı `OneriUreticiPort` sözleşmesi ve aynı prompt/şema/eşleme
(_oneri_ortak); yerel LLM çağrısı ve JSON zorlaması _yerel_llm'de ortaktır.
"""

from typing import Any

from app.adapters.cikan._llm_ayristir import dogrula_veya_bos
from app.adapters.cikan._oneri_ortak import (
    SISTEM_PROMPT,
    OneriListesi,
    maddeleri_onerilere_cevir,
)
from app.adapters.cikan._yerel_filtre import belirgin_sapmalar
from app.adapters.cikan._yerel_llm import json_talimati, yerel_calistir
from app.domain.modeller import Oneri

_SEMA = (
    '{"oneriler": [{"hat_id": int, "gun_no": int, "saat_baslangic": int, '
    '"oneri_metni": str, "gerekce": str}]}. '
    "Belirgin sapma yoksa oneriler boş liste olsun."
)


class SimpleOneriUreticisi:
    """OneriUreticiPort implementasyonu — yerel SimpleAgent ile."""

    def __init__(self, motor: Any, model: str) -> None:
        self._motor = motor
        self._model = model

    async def uret(self, ozet_veri: list[dict]) -> list[Oneri]:
        # Yerel model büyük girdide talimatı kaybediyor; yalnız belirgin sapmalar
        # gönderilir. Eşleme TAM veriye karşı yapılır ki hiçbir satır kaybolmasın.
        aday_veri = belirgin_sapmalar(ozet_veri)
        if not aday_veri:
            return []
        ham = yerel_calistir(
            self._motor, self._model, SISTEM_PROMPT + json_talimati(_SEMA), aday_veri
        )
        veri = dogrula_veya_bos(ham, OneriListesi, "oneriler")
        return maddeleri_onerilere_cevir(veri.oneriler, ozet_veri)
