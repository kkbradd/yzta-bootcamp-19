"""Depo sözleşmeleri — application katmanı yalnızca bu soyutlamalara konuşur."""

from datetime import datetime
from typing import Protocol

from app.domain.modeller import Arac, CihazAtamasi, HatAtamasi, Olcum


class OlcumDeposuPort(Protocol):
    async def ekle(self, olcum: Olcum) -> bool:
        """Ölçümü kalıcılaştırır; (cihaz_id, sira_no) mükerrerse False döner."""
        ...


class AtamaDeposuPort(Protocol):
    """Atama sorguları hep bir 'an'a görédir (zaman aralıklı tablolar, plan Bölüm 6)."""

    async def cihaz_atamasini_bul(self, cihaz_id: str, an: datetime) -> CihazAtamasi | None: ...

    async def hat_atamasini_bul(self, arac_id: int, an: datetime) -> HatAtamasi | None: ...

    async def arac_getir(self, arac_id: int) -> Arac | None: ...
