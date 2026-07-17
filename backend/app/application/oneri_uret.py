"""Haftalık örüntü tespiti → LLM yorumu → depoya yazma akışı (zamanlanmış tetiklenir)."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.domain.modeller import Oneri
from app.ports.oneri import OneriDeposuPort, OneriUreticiPort
from app.ports.sorgular import HaftalikOruntuSorgusuPort

logger = logging.getLogger(__name__)


def _karsilastirma_ekle(ozet: list[dict]) -> list[dict]:
    """Her (hat_id, saat_baslangic) grubu için kendi günü hariç diğer günlerin
    ortalamasını hesaplayıp 'karsilastirma_ortalama_doluluk' alanını ekler.
    """
    gruplar: dict[tuple[int, int], list[dict]] = {}
    for satir in ozet:
        anahtar = (satir["hat_id"], satir["saat_baslangic"])
        gruplar.setdefault(anahtar, []).append(satir)

    sonuc: list[dict] = []
    for satir in ozet:
        anahtar = (satir["hat_id"], satir["saat_baslangic"])
        diger_gunler = [
            s["ortalama_doluluk"] for s in gruplar[anahtar] if s["gun_no"] != satir["gun_no"]
        ]
        karsilastirma = sum(diger_gunler) / len(diger_gunler) if diger_gunler else None
        sonuc.append({**satir, "karsilastirma_ortalama_doluluk": karsilastirma})
    return sonuc


@dataclass(frozen=True, slots=True)
class OneriUret:
    sorgular: HaftalikOruntuSorgusuPort
    oneri_uretici: OneriUreticiPort
    oneri_deposu: OneriDeposuPort
    gun_pencere: int = 14

    async def calistir(self) -> list[Oneri]:
        bitis = datetime.now(UTC)
        baslangic = bitis - timedelta(days=self.gun_pencere)
        ozet = await self.sorgular.hat_haftalik_oruntu(baslangic, bitis)
        if not ozet:
            logger.info("öneri üretimi atlandı: yeterli veri yok")
            return []
        ozet_karsilastirmali = _karsilastirma_ekle(ozet)
        oneriler = await self.oneri_uretici.uret(ozet_karsilastirmali)
        if oneriler:
            await self.oneri_deposu.ekle(oneriler)
        return oneriler
