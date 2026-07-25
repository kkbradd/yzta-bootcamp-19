"""Video dosyasından kare okur; sona gelince başa sarar (kamera akışı taklidi).

Kareler gerçek zamanla orantılı ilerletilir: çıkarım yavaş olduğu için her kare
işlenmez, geçen süreye karşılık gelen kareye atlanır. Böylece video, çıkarım
maliyetinden bağımsız olarak gerçek zamanda akıyormuş gibi görünür.
"""

import logging
import time
from pathlib import Path

import cv2

from app.ayarlar import EdgeHatasi

logger = logging.getLogger("edge.video")

VARSAYILAN_FPS = 25.0  # dosya FPS bildirmezse


class VideoHatasi(EdgeHatasi):
    """Video okunamıyor — sessiz siyah kare yerine açık hata."""


class VideoKaynagi:
    """Döngüsel video okuyucu; kareyi modele verilecek boyuta küçültür."""

    def __init__(self, yol: Path, genislik: int, yukseklik: int) -> None:
        self._yol = yol
        self._genislik = genislik
        self._yukseklik = yukseklik
        self._yakalayici = cv2.VideoCapture(str(yol))
        if not self._yakalayici.isOpened():
            raise VideoHatasi(f"Video açılamadı: '{yol}'. Dosya ve codec desteğini kontrol edin.")
        self._fps = self._yakalayici.get(cv2.CAP_PROP_FPS) or VARSAYILAN_FPS
        self._kare_sayisi = int(self._yakalayici.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        self._baslangic = time.monotonic()
        logger.info("video açıldı: %s (%.1f fps, %d kare)", yol.name, self._fps, self._kare_sayisi)

    def kare_al(self):
        """Gerçek zamana karşılık gelen kareyi döndürür (BGR, küçültülmüş)."""
        self._hedef_kareye_atla()
        okundu, kare = self._yakalayici.read()
        if not okundu:
            okundu, kare = self._basa_sar()
        if not okundu:
            raise VideoHatasi(f"Video okunamıyor: '{self._yol}'. Dosya bozuk olabilir.")
        return cv2.resize(kare, (self._genislik, self._yukseklik))

    def _hedef_kareye_atla(self) -> None:
        gecen = time.monotonic() - self._baslangic
        hedef = int(gecen * self._fps) % self._kare_sayisi
        self._yakalayici.set(cv2.CAP_PROP_POS_FRAMES, hedef)

    def _basa_sar(self):
        self._yakalayici.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return self._yakalayici.read()

    def kapat(self) -> None:
        self._yakalayici.release()
