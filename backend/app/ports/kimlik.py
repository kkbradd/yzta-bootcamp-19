"""Kimlik doğrulama sözleşmeleri — depo (I/O) ve kriptografi (CPU-bound) ayrı tutulur."""

from typing import Protocol

from app.domain.modeller import Kullanici


class KullaniciDeposuPort(Protocol):
    async def epostaya_gore_bul(self, eposta: str) -> Kullanici | None: ...


class SifreleyiciPort(Protocol):
    def dogrula(self, duz_sifre: str, sifre_hash: str) -> bool: ...


class TokenUreticiPort(Protocol):
    def uret(self, kullanici_id: int, eposta: str) -> str: ...
