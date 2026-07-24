"""Periyodik konum üretimi: aktif her araç için KonumUret'i tetikleyen arka
plan görevi. Sonsuz uyku döngüsü, istisna görevi öldürmez (MqttIngest ile
aynı hata toleransı deseni).
"""

import asyncio
import logging

from app.application.konum_uret import KonumUret

logger = logging.getLogger(__name__)


class KonumZamanlayici:
    def __init__(self, konum_uret: KonumUret, periyot_sn: float = 2.0) -> None:
        self._konum_uret = konum_uret
        self._periyot_sn = periyot_sn

    async def calistir(self) -> None:
        while True:
            try:
                await self._konum_uret.tum_araclari_ilerlet()
            except Exception:
                logger.exception("konum üretimi sırasında beklenmeyen hata")
            await asyncio.sleep(self._periyot_sn)
