"""Gemini (google-genai) ile anlık durum yorumlama — SDK yalnız burada.

Prompt/şema/eşleme mantığı yerel üreticiyle ortaktır (_uyari_ortak); burada
yalnız bulut çağrısı yapılır.
"""

import json

from google import genai
from google.genai import types

from app.adapters.cikan._uyari_ortak import (
    SISTEM_PROMPT,
    UyariListesi,
    maddeleri_uyarilara_cevir,
)
from app.domain.modeller import Uyari


class GeminiUyariUreticisi:
    """UyariUreticiPort implementasyonu."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def uret(self, ozet_veri: list[dict]) -> list[Uyari]:
        if not ozet_veri:
            return []
        yanit = await self._client.aio.models.generate_content(
            model=self._model,
            contents="Aşağıdaki özet veriyi analiz et:\n\n" + json.dumps(ozet_veri, default=str),
            config=types.GenerateContentConfig(
                system_instruction=SISTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=UyariListesi,
            ),
        )
        veri = UyariListesi.model_validate_json(yanit.text)
        return maddeleri_uyarilara_cevir(veri.uyarilar, ozet_veri)
