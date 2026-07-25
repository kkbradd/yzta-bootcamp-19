"""Uyarı üretimi ve depolama sözleşmeleri."""

from typing import Protocol

from app.domain.modeller import Uyari


class UyariUreticiPort(Protocol):
    async def uret(self, ozet_veri: list[dict]) -> list[Uyari]:
        """SQL'den gelen özet satırlarını LLM'e yorumlatır; Uyari listesi döner."""
        ...


class UyariDeposuPort(Protocol):
    async def ekle(self, uyarilar: list[Uyari]) -> None: ...

    async def son_uyarilar(self, limit: int = 50) -> list[Uyari]: ...
