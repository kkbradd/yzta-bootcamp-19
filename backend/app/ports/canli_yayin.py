"""Canlı yayın sözleşmesi (WebSocket soyutlaması — plan Bölüm 8.5)."""

from datetime import datetime
from typing import Protocol

from app.domain.modeller import Olcum


class CanliYayinPort(Protocol):
    async def arac_guncellemesini_yayinla(self, olcum: Olcum) -> None: ...

    async def cihaz_durumunu_yayinla(
        self, cihaz_id: str, cevrimici: bool, son_gorulme: datetime | None
    ) -> None: ...
