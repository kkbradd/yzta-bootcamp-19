"""Kareden kişi sayısı kestirimi.

Normalizasyon şeması yazarın train.py'ındaki ImageNet normalizasyonudur. Deponun
val.ipynb'sindeki farklı şema ile ölçüldüğünde ağ saf gürültüden 55.9 kişi
halüsinasyonu üretiyor; bu yüzden şema burada sabittir ve entegrasyon testiyle
kilitlenmiştir (düz gri karede sayım ~0 çıkmalı).
"""

import logging
from pathlib import Path

import cv2
import numpy as np
import torch

from app.csrnet_agi import agi_yukle

logger = logging.getLogger("edge.csrnet")

IMAGENET_ORTALAMA = (0.485, 0.456, 0.406)
IMAGENET_STANDART_SAPMA = (0.229, 0.224, 0.225)
ORNEKLEME_CARPANI = 8  # ağ girdiyi 8 kat küçültür


def _tensore_cevir(kare_rgb: np.ndarray) -> torch.Tensor:
    """HWC uint8 RGB kareyi normalize edilmiş 1CHW tensöre çevirir.

    Boyutlar 8'in katına kırpılır: bölünebilirlik zorunlu değil (conv padding
    hallediyor) ama katı olmayan boyutta efektif adım 8'den kayar.
    """
    yukseklik = kare_rgb.shape[0] - kare_rgb.shape[0] % ORNEKLEME_CARPANI
    genislik = kare_rgb.shape[1] - kare_rgb.shape[1] % ORNEKLEME_CARPANI
    kirpilmis = kare_rgb[:yukseklik, :genislik]

    tensor = torch.from_numpy(np.ascontiguousarray(kirpilmis)).permute(2, 0, 1).float().div_(255.0)
    ortalama = torch.tensor(IMAGENET_ORTALAMA).view(3, 1, 1)
    standart_sapma = torch.tensor(IMAGENET_STANDART_SAPMA).view(3, 1, 1)
    return tensor.sub_(ortalama).div_(standart_sapma).unsqueeze(0)


class CsrnetKestirici:
    """Yüklü ağı saklar; her karede yoğunluk haritasının toplamını sayıya çevirir."""

    def __init__(self, agirlik_yolu: Path, is_parcacigi: int, sayim_carpani: float) -> None:
        torch.set_num_threads(is_parcacigi)
        self._ag = agi_yukle(agirlik_yolu)
        self._sayim_carpani = sayim_carpani
        logger.info("CSRNet yüklendi: %s (çarpan %.2f)", agirlik_yolu.name, sayim_carpani)

    def kestir(self, kare_bgr: np.ndarray) -> int:
        """OpenCV'den gelen BGR kare için tahmini kişi sayısı."""
        kare_rgb = cv2.cvtColor(kare_bgr, cv2.COLOR_BGR2RGB)
        ham_sayim = self._ham_sayim(kare_rgb)
        # Model otobüs içi için dağılım dışı; çarpan elle kalibrasyon içindir.
        # Ham değer de loglanır ki çarpanın etkisi ayırt edilebilsin.
        olceklenmis = ham_sayim * self._sayim_carpani
        logger.debug("ham sayım %.2f → ölçeklenmiş %.2f", ham_sayim, olceklenmis)
        # Son katman sınırsız: boş sahnede küçük negatif toplam çıkabilir ve
        # backend negatif kisi_sayisi'nı doğrulamada sessizce düşürür.
        return max(0, round(olceklenmis))

    def _ham_sayim(self, kare_rgb: np.ndarray) -> float:
        with torch.no_grad():
            yogunluk = self._ag(_tensore_cevir(kare_rgb))
        return float(yogunluk.sum())
