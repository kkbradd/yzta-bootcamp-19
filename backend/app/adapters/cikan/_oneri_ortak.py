"""Öneri üreticilerinin (Gemini + Simple/yerel) paylaştığı prompt, şema ve eşleme.

Motor (bulut/yerel) fark etmez; sistem promptu, LLM'den beklenen JSON şeması ve
LLM çıktısını gerçek özet satırıyla eşleyip `Oneri` domain nesnesine çevirme
mantığı ortaktır. Böylece iki üretici bu kuralları tekrarlamaz.
"""

import logging
from datetime import UTC, datetime

from pydantic import BaseModel

from app.domain.modeller import Oneri

logger = logging.getLogger(__name__)

SISTEM_PROMPT = (
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


class OneriMaddesi(BaseModel):
    hat_id: int
    gun_no: int
    saat_baslangic: int
    saat_bitis: int
    oneri_metni: str
    gerekce: str


class OneriListesi(BaseModel):
    oneriler: list[OneriMaddesi]


def _orijinal_satiri_bul(ozet_veri: list[dict], madde: OneriMaddesi) -> dict | None:
    for satir in ozet_veri:
        if (
            satir["hat_id"] == madde.hat_id
            and satir["gun_no"] == madde.gun_no
            and satir["saat_baslangic"] == madde.saat_baslangic
        ):
            return satir
    return None


def maddeleri_onerilere_cevir(maddeler: list[OneriMaddesi], ozet_veri: list[dict]) -> list[Oneri]:
    """LLM maddelerini gerçek özet satırıyla eşleyip Oneri'ye çevirir; uydurmaları atar."""
    simdi = datetime.now(UTC)
    oneriler = []
    for madde in maddeler:
        orijinal = _orijinal_satiri_bul(ozet_veri, madde)
        if orijinal is None:
            logger.warning("LLM bilinmeyen hat/gün/saat için öneri üretti, atlandı: %s", madde)
            continue
        oneriler.append(_madde_to_oneri(madde, orijinal, simdi))
    return oneriler


def _madde_to_oneri(madde: OneriMaddesi, orijinal: dict, simdi: datetime) -> Oneri:
    return Oneri(
        hat_id=madde.hat_id,
        gun_no=madde.gun_no,
        saat_baslangic=madde.saat_baslangic,
        saat_bitis=madde.saat_bitis,
        ortalama_doluluk=orijinal["ortalama_doluluk"],
        karsilastirma_ortalama_doluluk=orijinal.get("karsilastirma_ortalama_doluluk"),
        oneri_metni=madde.oneri_metni,
        gerekce=madde.gerekce,
        olusturulma_zamani=simdi,
    )
