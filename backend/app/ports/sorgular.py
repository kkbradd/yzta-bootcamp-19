"""Analitik sorgu sözleşmeleri — okuma odaklı, depolar.py'nin (yazma) dışında tutulur."""

from datetime import datetime
from typing import Protocol


class HaftalikOruntuSorgusuPort(Protocol):
    async def hat_haftalik_oruntu(
        self, baslangic: datetime, bitis: datetime, min_olcum_sayisi: int = 5
    ) -> list[dict]: ...


class AnlikOzetSorgusuPort(Protocol):
    async def hat_anlik_ozet(
        self, baslangic: datetime, bitis: datetime, min_olcum_sayisi: int = 3
    ) -> list[dict]: ...


class HatEslemeSorgusuPort(Protocol):
    async def hat_arac_cihaz_eslemelerini_al(self) -> list[dict]:
        """(hat_no, hat_id, arac_id, cihaz_id, kapasite) — güncel atamalardan okunur."""
        ...
