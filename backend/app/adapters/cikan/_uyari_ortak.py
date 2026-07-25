"""Uyarı üreticilerinin (Gemini + Simple/yerel) paylaştığı prompt, şema ve eşleme."""

import logging
from datetime import UTC, datetime

from pydantic import BaseModel

from app.domain.modeller import Uyari

logger = logging.getLogger(__name__)

SISTEM_PROMPT = (
    "Sen bir toplu taşıma operasyon analistisin. Sana hat bazında son birkaç "
    "saatlik ortalama doluluk oranı ve ortalama kişi sayısı verilecek. Her "
    "satırda hat_id (sayısal, yalnız eşleme için) ve hat_no (gerçek hat kodu, "
    "örn. '15A') bulunur. Uyarı metninde ve gerekçede hattan bahsederken "
    "MUTLAKA hat_no değerini kullan (örn. 'Hat 15A'), hat_id'yi asla metne "
    "yazma. Sana gelen hatların tamamı zaten yoğunluk eşiğini aşmış durumda — "
    "eşik kararını sen vermeyeceksin, sadece bu durumu operasyonel bir dille "
    "özetleyeceksin. Her hat için kısa, aksiyon alınabilir bir anlık durum "
    "uyarısı üret. Uyarı SADECE bir bilgilendirmedir, insan karar verecektir; "
    "'sefer sayısını X yap' gibi kesin sayısal talimat verme, 'ek sefer "
    "değerlendirilebilir' gibi yumuşak dil kullan."
)


class UyariMaddesi(BaseModel):
    hat_id: int
    uyari_metni: str
    gerekce: str


class UyariListesi(BaseModel):
    uyarilar: list[UyariMaddesi]


def _orijinal_hatti_bul(ozet_veri: list[dict], madde: UyariMaddesi) -> dict | None:
    for satir in ozet_veri:
        if satir["hat_id"] == madde.hat_id:
            return satir
    return None


def maddeleri_uyarilara_cevir(maddeler: list[UyariMaddesi], ozet_veri: list[dict]) -> list[Uyari]:
    """LLM maddelerini gerçek özet satırıyla eşleyip Uyari'ye çevirir; uydurmaları atar."""
    simdi = datetime.now(UTC)
    uyarilar = []
    for madde in maddeler:
        orijinal = _orijinal_hatti_bul(ozet_veri, madde)
        if orijinal is None:
            logger.warning("LLM bilinmeyen hat için uyarı üretti, atlandı: %s", madde)
            continue
        uyarilar.append(_madde_to_uyari(madde, orijinal, simdi))
    return uyarilar


def _madde_to_uyari(madde: UyariMaddesi, orijinal: dict, simdi: datetime) -> Uyari:
    return Uyari(
        hat_id=madde.hat_id,
        ortalama_doluluk=orijinal["ortalama_doluluk"],
        ortalama_kisi=orijinal["ortalama_kisi"],
        uyari_metni=madde.uyari_metni,
        gerekce=madde.gerekce,
        olusturulma_zamani=simdi,
    )
