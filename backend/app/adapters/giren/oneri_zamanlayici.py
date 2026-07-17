"""Zamanlanmış öneri üretimi: haftada bir (varsayılan Pazartesi 06:00) OneriUret'i
tetikleyen arka plan görevi. MqttIngest ile aynı desen: sonsuz uyku döngüsü,
istisna görevi öldürmez.
"""

import asyncio
import logging
from datetime import UTC, datetime

from app.application.oneri_uret import OneriUret

logger = logging.getLogger(__name__)

_KONTROL_PERIYODU_SN = 3600  # saatte bir "çalışma zamanı geldi mi" kontrolü


class OneriZamanlayici:
    def __init__(
        self, oneri_uret: OneriUret, calisma_gunu: int = 0, calisma_saati: int = 6
    ) -> None:
        """calisma_gunu: datetime.weekday() ile birebir (0=Pazartesi..6=Pazar)."""
        self._oneri_uret = oneri_uret
        self._calisma_gunu = calisma_gunu
        self._calisma_saati = calisma_saati
        self._son_calisma_haftasi: tuple[int, int] | None = None

    async def calistir(self) -> None:
        while True:
            try:
                await self._kontrol_et()
            except Exception:
                logger.exception("öneri zamanlayıcı kontrol hatası")
            await asyncio.sleep(_KONTROL_PERIYODU_SN)

    async def _kontrol_et(self) -> None:
        simdi = datetime.now(UTC)
        hafta_anahtari = simdi.isocalendar()[:2]  # (yil, hafta_no)
        zamani_geldi = (
            simdi.weekday() == self._calisma_gunu
            and simdi.hour >= self._calisma_saati
            and hafta_anahtari != self._son_calisma_haftasi
        )
        if not zamani_geldi:
            return
        logger.info("zamanlanmış öneri üretimi başlıyor")
        oneriler = await self._oneri_uret.calistir()
        logger.info("öneri üretimi tamamlandı, üretilen=%d", len(oneriler))
        self._son_calisma_haftasi = hafta_anahtari
