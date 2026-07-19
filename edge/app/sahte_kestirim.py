"""Modelsiz kestirici: boru hattını torch ve ağırlık olmadan test etmek için.

Sayı üretimi simulator/simulator.py ile aynı sinüs dalgasıdır; verilen kareyi
yok sayar. CSRNet kestiricisiyle aynı arayüzü (kestir) sunar.
"""

import math
import random
import time

TABAN_KAPASITE = 90  # edge_0001'in atandığı aracın kapasitesi (bkz. app/seed.py)
DALGA_PERIYODU_SN = 120
GURULTU_GENLIGI = 0.08
AZAMI_ORAN = 1.15  # aşırı doluluk da üretilebilsin


class SahteKestirici:
    """Kareye bakmadan, zamana göre salınan gerçekçi bir kişi sayısı üretir."""

    def __init__(self, taban_kapasite: int = TABAN_KAPASITE) -> None:
        self._taban_kapasite = taban_kapasite

    def kestir(self, kare: object) -> int:
        """Kare yok sayılır; imza CSRNet kestiricisiyle aynı kalsın diye durur."""
        dalga = (math.sin(time.monotonic() / DALGA_PERIYODU_SN) + 1) / 2
        gurultu = random.uniform(-GURULTU_GENLIGI, GURULTU_GENLIGI)
        oran = min(max(dalga + gurultu, 0.0), AZAMI_ORAN)
        return round(oran * self._taban_kapasite)
