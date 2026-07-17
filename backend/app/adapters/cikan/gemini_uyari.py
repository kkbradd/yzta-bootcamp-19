"""Gemini (google-genai) ile anlık durum yorumlama — SDK yalnız burada."""

import json
import logging
from datetime import UTC, datetime

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.domain.modeller import Uyari
from app.ports.uyari import UyariUreticiPort

logger = logging.getLogger(__name__)

_SISTEM_PROMPT = (
    "Sen bir toplu taşıma operasyon analistisin. Sana hat bazında son birkaç "
    "saatlik ortalama doluluk oranı ve ortalama kişi sayısı verilecek. "
    "Sana gelen hatların tamamı zaten yoğunluk eşiğini aşmış durumda — eşik "
    "kararını sen vermeyeceksin, sadece bu durumu operasyonel bir dille "
    "özetleyeceksin. Her hat için kısa, aksiyon alınabilir bir anlık durum "
    "uyarısı üret. Uyarı SADECE bir bilgilendirmedir, insan karar verecektir; "
    "'sefer sayısını X yap' gibi kesin sayısal talimat verme, 'ek sefer "
    "değerlendirilebilir' gibi yumuşak dil kullan."
)


class _UyariMaddesi(BaseModel):
    hat_id: int
    uyari_metni: str
    gerekce: str


class _UyariListesi(BaseModel):
    uyarilar: list[_UyariMaddesi]


def _orijinal_hatti_bul(ozet_veri: list[dict], u: _UyariMaddesi) -> dict | None:
    for satir in ozet_veri:
        if satir["hat_id"] == u.hat_id:
            return satir
    return None


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
                system_instruction=_SISTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=_UyariListesi,
            ),
        )
        veri = _UyariListesi.model_validate_json(yanit.text)
        simdi = datetime.now(UTC)

        uyarilar = []
        for u in veri.uyarilar:
            orijinal = _orijinal_hatti_bul(ozet_veri, u)
            if orijinal is None:
                logger.warning("LLM bilinmeyen hat için uyarı üretti, atlandı: %s", u)
                continue
            uyarilar.append(
                Uyari(
                    hat_id=u.hat_id,
                    ortalama_doluluk=orijinal["ortalama_doluluk"],
                    ortalama_kisi=orijinal["ortalama_kisi"],
                    uyari_metni=u.uyari_metni,
                    gerekce=u.gerekce,
                    olusturulma_zamani=simdi,
                )
            )
        return uyarilar
