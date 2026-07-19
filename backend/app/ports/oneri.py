"""Öneri üretimi ve depolama sözleşmeleri."""

from typing import Protocol

from app.domain.modeller import Oneri


class OneriUreticiPort(Protocol):
    async def uret(self, ozet_veri: list[dict]) -> list[Oneri]:
        """SQL'den gelen özet satırlarını LLM'e yorumlatır; Oneri listesi döner."""
        ...


class OneriDeposuPort(Protocol):
    async def ekle(self, oneriler: list[Oneri]) -> None: ...

    async def son_oneriler(self, limit: int = 50) -> list[Oneri]: ...
