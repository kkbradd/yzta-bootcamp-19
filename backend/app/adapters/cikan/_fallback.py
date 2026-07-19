"""Üretici fallback sarmalayıcı — asimetrik, gizlilik-öncelikli.

Birincil üretici hata verirse yedeğe düşer; AMA yalnız `yedege_izin=True` iken.
Yerel motor seçildiğinde `yedege_izin=False` verilir: Ollama düşse bile Gemini'ye
DÜŞÜLMEZ, böylece "lokal iste" diyen kullanıcının verisi Google'a sızmaz. Bulut
seçildiğinde yedek yereldir ve izin verilir (güvenli yön).
"""

import logging
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class _Uretici(Protocol):
    async def uret(self, ozet_veri: list[dict]) -> list[Any]: ...


class FallbackUretici:
    """Birincil üreticiyi dener; hata olursa yedeğe düşer.

    ``yedek`` None olabilir (yerel motorda Gemini yedeği hiç kurulmaz — gizlilik):
    o durumda birincil hatası boş sonuca çevrilir, dışarı veri gitmez.
    """

    def __init__(self, birincil: _Uretici, yedek: _Uretici | None) -> None:
        self._birincil = birincil
        self._yedek = yedek

    async def uret(self, ozet_veri: list[dict]) -> list[Any]:
        try:
            return await self._birincil.uret(ozet_veri)
        except Exception:
            logger.exception("birincil AI üreticisi başarısız")
            if self._yedek is None:
                logger.warning("yedek yok (gizlilik/yapılandırma), boş sonuç dönülüyor")
                return []
            logger.info("yedek AI üreticisine düşülüyor")
            return await self._yedek.uret(ozet_veri)
