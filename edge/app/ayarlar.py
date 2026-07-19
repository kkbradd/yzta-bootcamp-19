"""Edge cihaz servisi ayarları — tümü ortam değişkenlerinden okunur."""

import os
from dataclasses import dataclass
from pathlib import Path

CSRNET_MOTORU = "csrnet"
SAHTE_MOTOR = "sahte"
GECERLI_MOTORLAR = (CSRNET_MOTORU, SAHTE_MOTOR)

VARSAYILAN_CIHAZ_ID = "edge_0001"
VARSAYILAN_YAYIN_PERIYODU_SN = 2.0
VARSAYILAN_SAYIM_CARPANI = 1.0
VARSAYILAN_IS_PARCACIGI = 4
# 480x360 ölçülen CPU süresi ~1.3 sn; 2 sn'lik yayın periyoduna sığar (640x480 tek
# iş parçacığında 2.26 sn sürüyor ve periyodu aşıyor).
VARSAYILAN_GENISLIK = 480
VARSAYILAN_YUKSEKLIK = 360


class EdgeHatasi(Exception):
    """Servisin açılışta durmasını gerektiren, kullanıcıya anlatılabilir arıza.

    Ortak taban: giriş noktası yığın izi yerine tek satır hata basabilsin diye
    ayar/video/ağırlık arızaları bu türden türer.
    """


class EdgeAyarHatasi(EdgeHatasi, ValueError):
    """Ayarlar tutarsız — servis açılmadan önce fark edilir."""


def _sayi_oku(degisken: str, varsayilan: float) -> float:
    ham = os.getenv(degisken, "")
    if not ham:
        return varsayilan
    try:
        return float(ham)
    except ValueError as hata:
        raise EdgeAyarHatasi(f"{degisken} sayı olmalı, '{ham}' verildi.") from hata


@dataclass(frozen=True, slots=True)
class Ayarlar:
    motor: str
    video_yolu: Path
    agirlik_yolu: Path
    cihaz_id: str = VARSAYILAN_CIHAZ_ID
    broker: str = "localhost"
    port: int = 1883
    yayin_periyodu_sn: float = VARSAYILAN_YAYIN_PERIYODU_SN
    sayim_carpani: float = VARSAYILAN_SAYIM_CARPANI
    is_parcacigi: int = VARSAYILAN_IS_PARCACIGI
    genislik: int = VARSAYILAN_GENISLIK
    yukseklik: int = VARSAYILAN_YUKSEKLIK

    @property
    def csrnet_mi(self) -> bool:
        return self.motor == CSRNET_MOTORU

    @classmethod
    def ortamdan(cls) -> "Ayarlar":
        ayarlar = cls(
            motor=os.getenv("EDGE_MOTOR", SAHTE_MOTOR),
            video_yolu=Path(os.getenv("EDGE_VIDEO_YOLU", "")),
            agirlik_yolu=Path(os.getenv("EDGE_AGIRLIK_YOLU", "")),
            cihaz_id=os.getenv("EDGE_CIHAZ_ID", VARSAYILAN_CIHAZ_ID),
            broker=os.getenv("EDGE_BROKER", "localhost"),
            port=int(_sayi_oku("EDGE_PORT", 1883)),
            yayin_periyodu_sn=_sayi_oku("EDGE_YAYIN_PERIYODU_SN", VARSAYILAN_YAYIN_PERIYODU_SN),
            sayim_carpani=_sayi_oku("EDGE_SAYIM_CARPANI", VARSAYILAN_SAYIM_CARPANI),
            is_parcacigi=int(_sayi_oku("EDGE_IS_PARCACIGI", VARSAYILAN_IS_PARCACIGI)),
            genislik=int(_sayi_oku("EDGE_GENISLIK", VARSAYILAN_GENISLIK)),
            yukseklik=int(_sayi_oku("EDGE_YUKSEKLIK", VARSAYILAN_YUKSEKLIK)),
        )
        ayarlar._dogrula()
        return ayarlar

    def _dogrula(self) -> None:
        self._motoru_dogrula()
        self._periyodu_dogrula()
        if self.csrnet_mi:
            self._csrnet_girdilerini_dogrula()

    def _motoru_dogrula(self) -> None:
        if self.motor not in GECERLI_MOTORLAR:
            raise EdgeAyarHatasi(
                f"EDGE_MOTOR '{self.motor}' geçersiz; "
                f"geçerli değerler: {', '.join(GECERLI_MOTORLAR)}."
            )

    def _periyodu_dogrula(self) -> None:
        if self.yayin_periyodu_sn <= 0:
            raise EdgeAyarHatasi(
                f"EDGE_YAYIN_PERIYODU_SN pozitif olmalı, {self.yayin_periyodu_sn} verildi."
            )

    def _csrnet_girdilerini_dogrula(self) -> None:
        # 124 MB'lık modeli yükleyip sonra videonun olmadığını keşfetmektense önce patla.
        self._video_yolunu_dogrula()
        self._agirlik_yolunu_dogrula()

    def _video_yolunu_dogrula(self) -> None:
        if not self.video_yolu.name:
            raise EdgeAyarHatasi(
                f"EDGE_MOTOR={CSRNET_MOTORU} için EDGE_VIDEO_YOLU verilmedi. "
                "Videoyu edge/videolar/ altına koyup bu değişkeni ayarlayın."
            )
        if not self.video_yolu.is_file():
            raise EdgeAyarHatasi(
                f"EDGE_VIDEO_YOLU okunabilir bir dosya değil: '{self.video_yolu}'. "
                "Videoyu edge/videolar/ altına koyup yolu ayarlayın."
            )

    def _agirlik_yolunu_dogrula(self) -> None:
        eksik_dosya_notu = (
            "İndirme talimatı için model/README.md dosyasına bakın "
            f"veya modelsiz denemek için EDGE_MOTOR={SAHTE_MOTOR} kullanın."
        )
        if not self.agirlik_yolu.name:
            raise EdgeAyarHatasi(
                f"EDGE_MOTOR={CSRNET_MOTORU} için EDGE_AGIRLIK_YOLU verilmedi. {eksik_dosya_notu}"
            )
        if not self.agirlik_yolu.is_file():
            raise EdgeAyarHatasi(
                f"CSRNet ağırlığı bulunamadı: '{self.agirlik_yolu}'. {eksik_dosya_notu}"
            )
