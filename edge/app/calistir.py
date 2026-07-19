"""Edge servisi giriş noktası: video → kestirim → MQTT.

Çıkarım asyncio.to_thread ile ayrı bir iş parçacığında koşar. Doğrudan çağrılsaydı
CPU'da saniyeler süren forward pass event loop'u bloklar, MQTT keepalive'ı kaçırır
ve broker istemciyi düşürürdü; vasiyet tetiklenip backend cihazı tam çalışırken
çevrimdışı işaretlerdi (ağ arızası gibi görünen bir hata).
"""

import asyncio
import logging

import aiomqtt

from app.ayarlar import Ayarlar, EdgeHatasi
from app.yayinci import Yayinci, simdi, vasiyet_olustur

logger = logging.getLogger("edge")

YENIDEN_BAGLANMA_BEKLEMESI_SN = 3


def _kestirici_kur(ayarlar: Ayarlar):
    """CSRNet yalnız gerektiğinde import edilir: sahte mod torch'suz çalışsın."""
    if not ayarlar.csrnet_mi:
        from app.sahte_kestirim import SahteKestirici

        logger.info("sahte motor: kareler yok sayılıyor, sayılar üretiliyor")
        return SahteKestirici()

    from app.csrnet_kestirim import CsrnetKestirici

    return CsrnetKestirici(
        agirlik_yolu=ayarlar.agirlik_yolu,
        is_parcacigi=ayarlar.is_parcacigi,
        sayim_carpani=ayarlar.sayim_carpani,
    )


def _kaynak_kur(ayarlar: Ayarlar):
    """Sahte motorda video okunmaz; OpenCV kurulu olmadan da çalışabilsin."""
    if not ayarlar.csrnet_mi:
        return None

    from app.video_kaynagi import VideoKaynagi

    return VideoKaynagi(ayarlar.video_yolu, ayarlar.genislik, ayarlar.yukseklik)


async def _tur_yayinla(kaynak, kestirici, yayinci: Yayinci) -> None:
    """Bir kare al, sayımı yap, çekim damgasıyla yayınla."""
    kare = kaynak.kare_al() if kaynak is not None else None
    cekim_zamani = simdi()
    kisi_sayisi = await asyncio.to_thread(kestirici.kestir, kare)
    await yayinci.olcum_yayinla(kisi_sayisi, cekim_zamani)


async def _dongu(kaynak, kestirici, yayinci: Yayinci, periyot: float) -> None:
    saat = asyncio.get_running_loop().time
    while True:
        baslangic = saat()
        await _tur_yayinla(kaynak, kestirici, yayinci)
        gecen = saat() - baslangic
        # Çıkarım periyottan uzun sürdüyse bekleme yok: kaçan ölçümler biriktirilmez,
        # bayat sayıyı taze damgayla basmak trend sorgusunu bozardı.
        if gecen > periyot:
            logger.warning("çıkarım %.1f sn sürdü, yayın periyodu %.1f sn", gecen, periyot)
        await asyncio.sleep(max(periyot - gecen, 0))


async def calistir(ayarlar: Ayarlar) -> None:
    kestirici = _kestirici_kur(ayarlar)
    kaynak = _kaynak_kur(ayarlar)
    vasiyet = vasiyet_olustur(ayarlar.cihaz_id)

    while True:
        try:
            async with aiomqtt.Client(
                ayarlar.broker, port=ayarlar.port, will=vasiyet
            ) as istemci:
                yayinci = Yayinci(ayarlar.cihaz_id, istemci)
                await yayinci.cevrimici_bildir()
                await _dongu(kaynak, kestirici, yayinci, ayarlar.yayin_periyodu_sn)
        except aiomqtt.MqttError as hata:
            logger.warning(
                "broker bağlantısı koptu (%s), %s sn sonra yeniden denenecek",
                hata,
                YENIDEN_BAGLANMA_BEKLEMESI_SN,
            )
            await asyncio.sleep(YENIDEN_BAGLANMA_BEKLEMESI_SN)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        asyncio.run(calistir(Ayarlar.ortamdan()))
    except EdgeHatasi as hata:
        # Ayar/video/ağırlık arızası kullanıcı hatasıdır: yığın izi değil,
        # ne yapılacağını söyleyen tek satır bas.
        logger.error("%s", hata)
        raise SystemExit(1) from hata
    except KeyboardInterrupt:
        logger.info("edge servisi durduruldu")


if __name__ == "__main__":
    main()
