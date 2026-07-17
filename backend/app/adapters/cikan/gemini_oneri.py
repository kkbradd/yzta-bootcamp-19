"""Gemini (google-genai) ile örüntü yorumlama — SDK yalnız burada."""

import json
import logging
from datetime import UTC, datetime

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.domain.modeller import Oneri
from app.ports.oneri import OneriUreticiPort

logger = logging.getLogger(__name__)

_SISTEM_PROMPT = (
    "Sen bir toplu taşıma operasyon analistisin. Sana hat × haftanın günü × "
    "saat dilimi bazında ortalama doluluk verileri verilecek. gun_no alanı "
    "PostgreSQL EXTRACT(DOW) standardındadır: 0=Pazar, 1=Pazartesi, 2=Salı, "
    "3=Çarşamba, 4=Perşembe, 5=Cuma, 6=Cumartesi. Öneri metninde ve "
    "gerekçede günün adını yazarken mutlaka bu eşlemeyi kullan. Yalnızca "
    "istatistiksel olarak belirgin (diğer günlere göre gözle görülür sapma "
    "gösteren) örüntüler için kısa, aksiyon alınabilir bir operasyonel öneri "
    "üret. Öneri SADECE bir öneridir, insan karar verecektir; 'sefer sayısını "
    "X yap' gibi kesin sayısal talimat verme, 'artırmayı düşünün' gibi yumuşak "
    "dil kullan. Belirgin bir sapma yoksa o satır için öneri üretme."
)


class _OneriMaddesi(BaseModel):
    hat_id: int
    gun_no: int
    saat_baslangic: int
    saat_bitis: int
    oneri_metni: str
    gerekce: str


class _OneriListesi(BaseModel):
    oneriler: list[_OneriMaddesi]


def _orijinal_satiri_bul(ozet_veri: list[dict], o: _OneriMaddesi) -> dict | None:
    for satir in ozet_veri:
        if (
            satir["hat_id"] == o.hat_id
            and satir["gun_no"] == o.gun_no
            and satir["saat_baslangic"] == o.saat_baslangic
        ):
            return satir
    return None


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
                system_instruction=_SISTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=_OneriListesi,
            ),
        )
        veri = _OneriListesi.model_validate_json(yanit.text)
        simdi = datetime.now(UTC)

        oneriler = []
        for o in veri.oneriler:
            orijinal = _orijinal_satiri_bul(ozet_veri, o)
            if orijinal is None:
                logger.warning("LLM bilinmeyen hat/gün/saat için öneri üretti, atlandı: %s", o)
                continue
            oneriler.append(
                Oneri(
                    hat_id=o.hat_id,
                    gun_no=o.gun_no,
                    saat_baslangic=o.saat_baslangic,
                    saat_bitis=o.saat_bitis,
                    ortalama_doluluk=orijinal["ortalama_doluluk"],
                    karsilastirma_ortalama_doluluk=orijinal.get("karsilastirma_ortalama_doluluk"),
                    oneri_metni=o.oneri_metni,
                    gerekce=o.gerekce,
                    olusturulma_zamani=simdi,
                )
            )
        return oneriler
