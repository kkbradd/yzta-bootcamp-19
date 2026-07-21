"""Konum üretimi için okuma sözleşmesi — hangi araç hangi hatta, ve o hattın güzergahı."""

from typing import Protocol

from app.domain.modeller import Guzergah


class GuzergahSorgusuPort(Protocol):
    async def aktif_hat_atamalarini_listele(self) -> list[tuple[int, int]]:
        """(arac_id, hat_id) çiftlerini döner — yalnız bitis IS NULL atamalar."""
        ...

    async def hat_guzergahini_getir(self, hat_id: int) -> Guzergah | None: ...
