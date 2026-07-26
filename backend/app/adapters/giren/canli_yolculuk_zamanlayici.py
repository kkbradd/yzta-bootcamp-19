"""Periyodik canlı yolculuk üretimi: sefer zamanı gelmiş hatları tetikleyen
arka plan görevi. Sonsuz uyku döngüsü, istisna görevi öldürmez (KonumZamanlayici
ile aynı hata toleransı deseni).
"""

import asyncio
import logging

from app.application.canli_yolculuk_uret import CanliYolculukUret

logger = logging.getLogger(__name__)


class CanliYolculukZamanlayici:
    def __init__(self, canli_yolculuk_uret: CanliYolculukUret, periyot_sn: float = 5.0) -> None:
        self._canli_yolculuk_uret = canli_yolculuk_uret
        self._periyot_sn = periyot_sn

    async def calistir(self) -> None:
        while True:
            try:
                await self._canli_yolculuk_uret.tetikle()
            except Exception:
                logger.exception("canlı yolculuk üretimi sırasında beklenmeyen hata")
            await asyncio.sleep(self._periyot_sn)
