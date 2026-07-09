"""Sahte edge cihaz simülatörü (plan Bölüm 10/Faz 5).

N sahte cihaz, periyodik olarak gerçekçi kişi sayıları üretip MQTT'ye yayınlar.

Örnekler:
  python simulator/simulator.py --cihaz 3                 # 3 cihaz, 5 sn periyot
  python simulator/simulator.py --cihaz 1 --tunel 60      # 60 sn tünel modu
  python simulator/simulator.py --periyot 2 --broker localhost

Tünel modu: cihaz --tunel saniyesi boyunca yayın yapmaz (4G kesintisi taklidi),
ölçümleri çekim damgalarıyla biriktirir; süre dolunca hepsini artan sira_no ile
tek seferde boşaltır. Backend bunları geldiği ana değil, damgalarındaki ana yazar.

LWT: bağlanırken {"cevrimici": false} vasiyeti bırakılır (retained); süreç
kill -9 ile ölürse broker bunu kendisi yayınlar — backend cihazı çevrimdışı işaretler.
"""

import argparse
import asyncio
import json
import logging
import math
import random
import time
from datetime import UTC, datetime

import aiomqtt

logger = logging.getLogger("simulator")

YAZILIM_SURUMU = "1.2.0"
TABAN_KAPASITE = 90  # üretilen sayılar bu ölçeğe göre salınır


def _gerceklesen_sayi(cihaz_no: int, an: float) -> int:
    """Sinüs dalgası + gürültü: boş ↔ yoğun arasında yavaşça salınan kişi sayısı."""
    faz = cihaz_no * 1.7  # cihazlar aynı anda dolup boşalmasın
    dalga = (math.sin(an / 120 + faz) + 1) / 2  # 0..1, ~12 dk periyot
    gurultu = random.uniform(-0.08, 0.08)
    oran = min(max(dalga + gurultu, 0.0), 1.15)  # aşırı doluluk da üretilebilsin
    return round(oran * TABAN_KAPASITE)


async def cihaz_calistir(
    cihaz_no: int, broker: str, port: int, periyot: float, tunel_sn: float
) -> None:
    cihaz_id = f"edge_{cihaz_no:04d}"
    durum_topic = f"filo/{cihaz_id}/durum"
    yogunluk_topic = f"filo/{cihaz_id}/yogunluk"
    vasiyet = aiomqtt.Will(
        topic=durum_topic, payload=json.dumps({"cevrimici": False}), qos=1, retain=True
    )

    # Gerçek cihazın kalıcı sayacını taklit et: çalıştırmalar arası monoton kalsın,
    # yoksa yeniden başlatılan simülatörün tüm ölçümleri UNIQUE(cihaz_id, sira_no)
    # nedeniyle mükerrer sayılır.
    sira_no = int(time.time())
    bekleyenler: list[dict] = []
    tunel_bitisi = time.monotonic() + tunel_sn if tunel_sn > 0 else None

    async with aiomqtt.Client(broker, port=port, will=vasiyet) as istemci:
        await istemci.publish(
            durum_topic,
            json.dumps({"cevrimici": True, "yazilim_surumu": YAZILIM_SURUMU}),
            qos=1,
            retain=True,
        )
        logger.info("%s bağlandı (tünel: %s sn)", cihaz_id, tunel_sn or "yok")

        while True:
            sira_no += 1
            olcum = {
                "sira_no": sira_no,
                "kisi_sayisi": _gerceklesen_sayi(cihaz_no, time.monotonic()),
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

            if tunel_bitisi is not None and time.monotonic() < tunel_bitisi:
                bekleyenler.append(olcum)  # tüneldeyiz: biriktir, yayınlama
            else:
                if bekleyenler:
                    logger.info(
                        "%s tünelden çıktı, %d birikmiş ölçüm boşaltılıyor",
                        cihaz_id,
                        len(bekleyenler),
                    )
                    for bekleyen in bekleyenler:
                        await istemci.publish(yogunluk_topic, json.dumps(bekleyen), qos=1)
                    bekleyenler.clear()
                    tunel_bitisi = None
                await istemci.publish(yogunluk_topic, json.dumps(olcum), qos=1)
                logger.info(
                    "%s → kisi_sayisi=%s sira_no=%s", cihaz_id, olcum["kisi_sayisi"], sira_no
                )

            await asyncio.sleep(periyot)


async def calistir(argumanlar: argparse.Namespace) -> None:
    gorevler = [
        cihaz_calistir(
            cihaz_no, argumanlar.broker, argumanlar.port, argumanlar.periyot, argumanlar.tunel
        )
        for cihaz_no in range(1, argumanlar.cihaz + 1)
    ]
    await asyncio.gather(*gorevler)


def _argumanlari_ayristir() -> argparse.Namespace:
    ayristirici = argparse.ArgumentParser(description="HAT 01 sahte edge cihaz simülatörü")
    ayristirici.add_argument("--cihaz", type=int, default=3, help="cihaz sayısı (edge_0001..N)")
    ayristirici.add_argument("--periyot", type=float, default=5.0, help="yayın periyodu (sn)")
    ayristirici.add_argument(
        "--tunel", type=float, default=0.0, help="başlangıçta tünel modu süresi (sn)"
    )
    ayristirici.add_argument("--broker", default="localhost")
    ayristirici.add_argument("--port", type=int, default=1883)
    return ayristirici.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        asyncio.run(calistir(_argumanlari_ayristir()))
    except KeyboardInterrupt:
        logger.info("simülatör durduruldu")
