"""CSRNet ağ tanımı ve ağırlık yükleme (Li et al., CVPR 2018).

VGG16 önyüzü (conv4_3'e kadar, 10 conv) + genişletilmiş (dilated) arka uç.
Çıktı, girdinin 1/8 çözünürlüğünde bir yoğunluk haritasıdır.

Katman isimlendirmesi leeyeehoo/CSRNet-pytorch ile birebir aynı olmalıdır; aksi
halde strict yükleme anahtar uyuşmazlığıyla patlar (sessizce çöp üretmemesi için
strict=True bilinçli seçimdir).
"""

from pathlib import Path

import torch
from torch import nn

from app.ayarlar import EdgeHatasi

ONYUZ_YAPISI = [64, 64, "M", 128, 128, "M", 256, 256, 256, "M", 512, 512, 512]
ARKAUC_YAPISI = [512, 512, 512, 256, 128, 64]
ARKAUC_GENISLETME = 2
HAVUZ = "M"


class AgirlikHatasi(EdgeHatasi):
    """Ağırlık dosyası okunamıyor veya ağla uyuşmuyor."""


def _katmanlari_kur(yapi: list, giris_kanali: int, genisletme: int) -> nn.Sequential:
    katmanlar: list[nn.Module] = []
    for kanal in yapi:
        if kanal == HAVUZ:
            katmanlar.append(nn.MaxPool2d(kernel_size=2, stride=2))
            continue
        katmanlar.append(
            nn.Conv2d(giris_kanali, kanal, kernel_size=3, padding=genisletme, dilation=genisletme)
        )
        katmanlar.append(nn.ReLU(inplace=True))
        giris_kanali = kanal
    return nn.Sequential(*katmanlar)


class Csrnet(nn.Module):
    """Yoğunluk haritası üreten sayım ağı (16.263.489 parametre)."""

    def __init__(self) -> None:
        super().__init__()
        self.frontend = _katmanlari_kur(ONYUZ_YAPISI, giris_kanali=3, genisletme=1)
        self.backend = _katmanlari_kur(
            ARKAUC_YAPISI, giris_kanali=512, genisletme=ARKAUC_GENISLETME
        )
        self.output_layer = nn.Conv2d(64, 1, kernel_size=1)

    def forward(self, goruntuler: torch.Tensor) -> torch.Tensor:
        return self.output_layer(self.backend(self.frontend(goruntuler)))


def _durum_sozlugu_cikar(kontrol_noktasi: object) -> dict:
    """Eğitim checkpoint'ini açar ve DataParallel önekini soyar.

    .pth.tar dosyaları state_dict/epoch/optimizer ile sarılıdır; HuggingFace
    kopyaları çıplak OrderedDict'tir. İkisi de desteklenir.
    """
    durum = (
        kontrol_noktasi.get("state_dict", kontrol_noktasi)
        if isinstance(kontrol_noktasi, dict)
        else kontrol_noktasi
    )
    return {anahtar.replace("module.", "", 1): deger for anahtar, deger in durum.items()}


def agi_yukle(agirlik_yolu: Path) -> Csrnet:
    """Ağırlığı okuyup değerlendirme moduna alınmış ağı döndürür."""
    if not agirlik_yolu.is_file():
        raise AgirlikHatasi(f"CSRNet ağırlığı bulunamadı: '{agirlik_yolu}'.")
    try:
        # weights_only=False şart: bu checkpoint numpy nesneleriyle serileştirilmiş,
        # torch>=2.6'nın güvenli varsayılanı okumayı reddeder.
        kontrol_noktasi = torch.load(agirlik_yolu, map_location="cpu", weights_only=False)
    except Exception as hata:
        raise AgirlikHatasi(
            f"Ağırlık okunamadı: '{agirlik_yolu}'. Dosya bozuk olabilir "
            "(indirme sırasında HTML hata sayfası kaydedilmiş olabilir)."
        ) from hata

    ag = Csrnet()
    try:
        ag.load_state_dict(_durum_sozlugu_cikar(kontrol_noktasi), strict=True)
    except (RuntimeError, AttributeError) as hata:
        raise AgirlikHatasi(
            f"Ağırlık bu ağla uyuşmuyor: '{agirlik_yolu}'. CSRNet checkpoint'i mi?"
        ) from hata
    ag.eval()
    return ag
