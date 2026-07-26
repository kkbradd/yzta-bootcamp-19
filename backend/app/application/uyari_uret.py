"""Anlık durum tespiti → LLM yorumu → depoya yazma akışı (zamanlanmış tetiklenir).

Öneri akışından farkı: geçmiş örüntü değil, son N saatlik ham veriye bakar;
yalnızca mevcut seviye eşiklerini aşan (yoğun) hatlar LLM'e gönderilir.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.application.olcum_isle import SeviyeEsikleri
from app.domain.modeller import Uyari
from app.domain.seviye import SEVIYE_YOGUN, seviye_belirle
from app.ports.sorgular import AnlikOzetSorgusuPort
from app.ports.uyari import UyariDeposuPort, UyariUreticiPort

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class UyariUret:
    sorgular: AnlikOzetSorgusuPort
    uyari_uretici: UyariUreticiPort
    uyari_deposu: UyariDeposuPort
    esikler: SeviyeEsikleri
    saat_pencere: int = 3

    async def calistir(self) -> list[Uyari]:
        bitis = datetime.now(UTC)
        baslangic = bitis - timedelta(hours=self.saat_pencere)
        ozet = await self.sorgular.hat_anlik_ozet(baslangic, bitis)
        yogun_ozet = [
            s
            for s in ozet
            if seviye_belirle(s["ortalama_doluluk"], self.esikler.seyrek_ust, self.esikler.orta_ust)
            == SEVIYE_YOGUN
        ]
        if not yogun_ozet:
            logger.info("uyarı üretimi atlandı: yoğun hat yok")
            return []

        # Aynı hat, uyarı penceresi içinde zaten bir uyarı almışsa tekrar LLM'e
        # gönderilmez: yoğunluk uzun sürdüğünde her tetiklemede neredeyse aynı
        # anlamda yeni bir metin üretilip aynı hat için tekrar tekrar kart
        # birikmesin diye (gereksiz LLM çağrısı da önlenir).
        son_uyarilar = await self.uyari_deposu.son_uyarilar()
        uyarili_hat_idleri = {
            u.hat_id
            for u in son_uyarilar
            if u.olusturulma_zamani >= bitis - timedelta(hours=self.saat_pencere)
        }
        yeni_yogun_ozet = [s for s in yogun_ozet if s["hat_id"] not in uyarili_hat_idleri]
        if not yeni_yogun_ozet:
            logger.info("uyarı üretimi atlandı: yoğun hatların hepsi zaten uyarılı")
            return []

        uyarilar = await self.uyari_uretici.uret(yeni_yogun_ozet)
        if uyarilar:
            await self.uyari_deposu.ekle(uyarilar)
        return uyarilar
