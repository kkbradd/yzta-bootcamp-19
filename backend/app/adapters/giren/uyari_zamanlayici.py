"""Periyodik uyarı üretimi: sabit periyotta (varsayılan 3 saatte bir) UyariUret'i
tetikleyen arka plan görevi. MqttIngest ile aynı desen: sonsuz uyku döngüsü,
istisna görevi öldürmez. Öneri zamanlayıcısından farklı olarak haftalık bariyer
yok — her periyotta koşulsuz çalışır.
"""

import asyncio
import logging

from app.application.uyari_uret import UyariUret

logger = logging.getLogger(__name__)


class UyariZamanlayici:
    def __init__(self, uyari_uret: UyariUret, periyot_sn: int = 10800) -> None:
        self._uyari_uret = uyari_uret
        self._periyot_sn = periyot_sn

    async def calistir(self) -> None:
        while True:
            try:
                uyarilar = await self._uyari_uret.calistir()
                logger.info("uyarı üretimi tamamlandı, üretilen=%d", len(uyarilar))
            except Exception:
                logger.exception("uyarı zamanlayıcı hatası")
            await asyncio.sleep(self._periyot_sn)
