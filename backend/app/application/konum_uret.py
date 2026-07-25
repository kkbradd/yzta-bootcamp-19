"""Aktif hat atamalı her araç için güzergah üzerinde konum ilerletir.

Doluluk (Olcum) pipeline'ından tamamen bağımsızdır — mevcut arac_guncelleme
akışına dokunmaz, ayrı bir WS mesaj tipi (arac_konum) kullanır. Bellek-içi
durum: her araç için son yüzde (0.0-1.0) tutulur — süreç yeniden başlarsa
baştan başlar (kabul edilebilir, kalıcı durum gerektirmez).
"""

from dataclasses import dataclass, field

from app.ports.canli_yayin import CanliYayinPort
from app.ports.guzergah import GuzergahSorgusuPort


def _interpolasyon(koordinatlar: list[tuple[float, float]], yuzde: float) -> tuple[float, float]:
    n = len(koordinatlar) - 1
    konum = yuzde * n
    i = int(konum)
    if i >= n:
        return koordinatlar[-1]
    t = konum - i
    lat1, lon1 = koordinatlar[i]
    lat2, lon2 = koordinatlar[i + 1]
    return (lat1 + (lat2 - lat1) * t, lon1 + (lon2 - lon1) * t)


@dataclass(slots=True)
class KonumUret:
    guzergah_sorgusu: GuzergahSorgusuPort
    canli_yayin: CanliYayinPort
    adim_orani: float = 0.02  # her tetiklemede yüzde ilerleme (hız ayarı)
    _yuzdeler: dict[int, float] = field(default_factory=dict)

    async def tum_araclari_ilerlet(self) -> None:
        aktif_araclar = await self.guzergah_sorgusu.aktif_hat_atamalarini_listele()
        for arac_id, hat_id in aktif_araclar:
            guzergah = await self.guzergah_sorgusu.hat_guzergahini_getir(hat_id)
            if guzergah is None or len(guzergah.koordinatlar) < 2:
                continue
            yuzde = (self._yuzdeler.get(arac_id, 0.0) + self.adim_orani) % 1.0
            self._yuzdeler[arac_id] = yuzde
            enlem, boylam = _interpolasyon(guzergah.koordinatlar, yuzde)
            await self.canli_yayin.arac_konumunu_yayinla(arac_id, hat_id, enlem, boylam)
