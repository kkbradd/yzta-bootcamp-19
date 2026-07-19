"""Ölçümleri MQTT'ye yayınlar (sözleşme: docs/mqtt.md).

Yayın kuralları sessiz veri kaybını önlemek için birebir uyulması gerekenlerdir:
  - alan adı `timestamp` (olcum_zamani değil), yoksa backend mesajı doğrulamada düşürür
  - damga çekim anına ait olmalı: cihaz→araç→hat eşlemesi o ana göre çözülür
  - (cihaz_id, sira_no) çifti tekrar ederse backend mesajı sessizce yutar
"""

import json
import logging
import time
from datetime import UTC, datetime

import aiomqtt

logger = logging.getLogger("edge.yayinci")

YAZILIM_SURUMU = "2.0.0"
DAMGA_BICIMI = "%Y-%m-%dT%H:%M:%SZ"


class Yayinci:
    """Tek cihazın MQTT oturumu: vasiyet, çevrimiçi durumu ve ölçüm yayını."""

    def __init__(self, cihaz_id: str, istemci: aiomqtt.Client) -> None:
        self._cihaz_id = cihaz_id
        self._istemci = istemci
        self._durum_topic = f"filo/{cihaz_id}/durum"
        self._yogunluk_topic = f"filo/{cihaz_id}/yogunluk"
        # Gerçek cihazın kalıcı sayacını taklit et: çalıştırmalar arası monoton
        # kalsın, yoksa yeniden başlatılan servisin ölçümleri mükerrer sayılır.
        self._sira_no = int(time.time())

    async def cevrimici_bildir(self) -> None:
        await self._istemci.publish(
            self._durum_topic,
            json.dumps({"cevrimici": True, "yazilim_surumu": YAZILIM_SURUMU}),
            qos=1,
            retain=True,
        )
        logger.info("%s bağlandı", self._cihaz_id)

    async def olcum_yayinla(self, kisi_sayisi: int, cekim_zamani: datetime) -> None:
        self._sira_no += 1
        olcum = {
            "sira_no": self._sira_no,
            "kisi_sayisi": kisi_sayisi,
            "timestamp": cekim_zamani.strftime(DAMGA_BICIMI),
        }
        await self._istemci.publish(self._yogunluk_topic, json.dumps(olcum), qos=1)
        logger.info(
            "%s → kisi_sayisi=%s sira_no=%s", self._cihaz_id, kisi_sayisi, self._sira_no
        )


def vasiyet_olustur(cihaz_id: str) -> aiomqtt.Will:
    """Süreç kill -9 ile ölürse broker cihazı çevrimdışı ilan etsin."""
    return aiomqtt.Will(
        topic=f"filo/{cihaz_id}/durum",
        payload=json.dumps({"cevrimici": False}),
        qos=1,
        retain=True,
    )


def simdi() -> datetime:
    return datetime.now(UTC)
