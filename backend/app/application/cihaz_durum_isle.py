"""Cihaz durum mesajı akışı (plan Bölüm 8.4-8.5): anlık duruma yaz + yayınla."""

from dataclasses import dataclass
from datetime import datetime

from app.ports.anlik_durum import AnlikDurumPort
from app.ports.canli_yayin import CanliYayinPort


@dataclass(frozen=True, slots=True)
class CihazDurumIsleyici:
    anlik_durum: AnlikDurumPort
    canli_yayin: CanliYayinPort

    async def isle(
        self,
        cihaz_id: str,
        cevrimici: bool,
        yazilim_surumu: str | None,
        son_gorulme: datetime | None,
    ) -> None:
        """son_gorulme None ise anlık durumdaki mevcut değer korunur."""
        await self.anlik_durum.cihaz_durumunu_yaz(cihaz_id, cevrimici, yazilim_surumu, son_gorulme)
        await self.canli_yayin.cihaz_durumunu_yayinla(cihaz_id, cevrimici, son_gorulme)
