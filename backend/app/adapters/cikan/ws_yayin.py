"""CanliYayinPort'un WebSocket implementasyonu: bağlantı yöneticisi + yayın.

Mesaj sözleşmesi (plan Bölüm 8.5/9):
  {"tip": "arac_guncelleme", arac_id, hat_id, kisi_sayisi, doluluk_orani, seviye, zaman}
  {"tip": "cihaz_durum", cihaz_id, cevrimici, son_gorulme}
Kopan istemci yayını bozmaz; ilk gönderim hatasında sessizce düşürülür.
"""

import logging
from datetime import datetime
from typing import Protocol

from app.domain.modeller import Olcum

logger = logging.getLogger(__name__)


class YayinBaglantisi(Protocol):
    """Yöneticinin ihtiyaç duyduğu asgari WebSocket yüzeyi (test edilebilirlik)."""

    async def accept(self) -> None: ...

    async def send_json(self, mesaj: dict) -> None: ...


class BaglantiYoneticisi:
    def __init__(self) -> None:
        self._baglantilar: set[YayinBaglantisi] = set()

    @property
    def baglanti_sayisi(self) -> int:
        return len(self._baglantilar)

    async def baglan(self, baglanti: YayinBaglantisi) -> None:
        await baglanti.accept()
        self._baglantilar.add(baglanti)

    def kopar(self, baglanti: YayinBaglantisi) -> None:
        self._baglantilar.discard(baglanti)

    async def _yayinla(self, mesaj: dict) -> None:
        for baglanti in list(self._baglantilar):
            try:
                await baglanti.send_json(mesaj)
            except Exception:  # gönderilemeyen istemci koptu sayılır
                logger.info("istemci yayın sırasında düştü, bağlantı kaldırıldı")
                self.kopar(baglanti)

    # ---- CanliYayinPort ----

    async def arac_guncellemesini_yayinla(self, olcum: Olcum) -> None:
        await self._yayinla(
            {
                "tip": "arac_guncelleme",
                "arac_id": olcum.arac_id,
                "hat_id": olcum.hat_id,
                "kisi_sayisi": olcum.kisi_sayisi,
                "doluluk_orani": olcum.doluluk_orani,
                "seviye": olcum.seviye,
                "zaman": olcum.olcum_zamani.isoformat(),
            }
        )

    async def cihaz_durumunu_yayinla(
        self, cihaz_id: str, cevrimici: bool, son_gorulme: datetime | None
    ) -> None:
        await self._yayinla(
            {
                "tip": "cihaz_durum",
                "cihaz_id": cihaz_id,
                "cevrimici": cevrimici,
                "son_gorulme": son_gorulme.isoformat() if son_gorulme else None,
            }
        )
