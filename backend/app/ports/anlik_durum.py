"""Anlık durum sözleşmesi (Redis soyutlaması — plan Bölüm 8.3-8.4)."""

from datetime import datetime
from typing import Protocol

from app.domain.modeller import Olcum


class AnlikDurumPort(Protocol):
    async def arac_durumunu_yaz(self, olcum: Olcum) -> None:
        """Araç ölçümünün anlık durumunu günceller (olcum.arac_id doludur)."""
        ...

    async def cihaz_durumunu_yaz(
        self,
        cihaz_id: str,
        cevrimici: bool,
        yazilim_surumu: str | None,
        son_gorulme: datetime | None,
    ) -> None:
        """son_gorulme None ise mevcut değer korunur (retained tekrar oynatma)."""
        ...
