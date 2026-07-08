"""MQTT giren adaptörü.

Faz 0'da yalnızca broker sağlık kontrolü içerir; ölçüm/durum aboneliği
(filo/+/yogunluk, filo/+/durum) Faz 2'de bu modüle eklenecek.
"""

import aiomqtt

from app.ayarlar import Ayarlar

_SAGLIK_KONTROL_ZAMAN_ASIMI_SN = 3


async def mqtt_saglikli(ayarlar: Ayarlar) -> bool:
    async with aiomqtt.Client(
        ayarlar.mqtt_host, port=ayarlar.mqtt_port, timeout=_SAGLIK_KONTROL_ZAMAN_ASIMI_SN
    ):
        return True
