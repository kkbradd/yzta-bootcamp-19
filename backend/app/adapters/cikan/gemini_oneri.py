"""Gemini (google-genai) ile örüntü yorumlama — SDK yalnız burada.

Prompt/şema/eşleme mantığı yerel üreticiyle ortaktır (_oneri_ortak); burada
yalnız bulut çağrısı yapılır. Şema, Gemini'de API düzeyinde zorlanır
(response_schema), yerelde ise prompta yazılır (bkz. simple_oneri).
"""

import json

from google import genai
from google.genai import types

from app.adapters.cikan._oneri_ortak import (
    SISTEM_PROMPT,
    OneriListesi,
    maddeleri_onerilere_cevir,
)
from app.domain.modeller import Oneri


class GeminiOneriUreticisi:
    """OneriUreticiPort implementasyonu."""

    def __init__(self, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def uret(self, ozet_veri: list[dict]) -> list[Oneri]:
        if not ozet_veri:
            return []
        yanit = await self._client.aio.models.generate_content(
            model=self._model,
            contents="Aşağıdaki özet veriyi analiz et:\n\n" + json.dumps(ozet_veri, default=str),
            config=types.GenerateContentConfig(
                system_instruction=SISTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=OneriListesi,
            ),
        )
        veri = OneriListesi.model_validate_json(yanit.text)
        return maddeleri_onerilere_cevir(veri.oneriler, ozet_veri)
