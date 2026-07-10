"""MQTT giren adaptörü: filo/+/yogunluk ve filo/+/durum akışlarını dinler
(plan Bölüm 7) ve use-case'leri tetikler.

Hata politikası iki ayrı sınırla uygulanır:
- parse/doğrulama hatası = bozuk mesaj → uyarı logla, düşür;
- işleme (dispatch) hatası = beklenmeyen → hata logla, akış DURMAZ.
Sağlık kontrolü, her istekte yeni bağlantı açmak yerine bu görevin
bağlantı durumunu raporlar.
"""

import asyncio
import json
import logging
from datetime import UTC, datetime

import aiomqtt
from pydantic import BaseModel, Field, ValidationError

from app.application.cihaz_durum_isle import CihazDurumIsleyici
from app.application.olcum_isle import OlcumIsleyici
from app.ayarlar import Ayarlar

logger = logging.getLogger(__name__)

_YENIDEN_BAGLANMA_BEKLEMESI_SN = 3
_YOGUNLUK_TOPIC = "filo/+/yogunluk"
_DURUM_TOPIC = "filo/+/durum"


class YogunlukMesaji(BaseModel):
    """filo/{cihaz_id}/yogunluk yükü; timestamp çekim anıdır (plan Bölüm 7)."""

    sira_no: int
    kisi_sayisi: int = Field(ge=0)
    timestamp: datetime


class DurumMesaji(BaseModel):
    """filo/{cihaz_id}/durum yükü (LWT dahil)."""

    cevrimici: bool
    yazilim_surumu: str | None = None


class MqttIngest:
    def __init__(
        self,
        ayarlar: Ayarlar,
        olcum_isleyici: OlcumIsleyici,
        cihaz_durum_isleyici: CihazDurumIsleyici,
    ) -> None:
        self._ayarlar = ayarlar
        self._olcum_isleyici = olcum_isleyici
        self._cihaz_durum_isleyici = cihaz_durum_isleyici
        self._bagli = False

    async def saglikli(self) -> bool:
        return self._bagli

    async def calistir(self) -> None:
        """Kopana dek dinler; kopunca bekleyip yeniden bağlanır (lifespan görevi)."""
        while True:
            try:
                async with aiomqtt.Client(
                    self._ayarlar.mqtt_host, port=self._ayarlar.mqtt_port
                ) as istemci:
                    self._bagli = True
                    logger.info("MQTT bağlandı host=%s", self._ayarlar.mqtt_host)
                    await istemci.subscribe(_YOGUNLUK_TOPIC, qos=1)
                    await istemci.subscribe(_DURUM_TOPIC, qos=1)
                    async for mesaj in istemci.messages:
                        await self._mesaji_isle(mesaj)
            except aiomqtt.MqttError as hata:
                logger.warning(
                    "MQTT bağlantısı koptu, %s sn sonra yeniden denenecek: %s",
                    _YENIDEN_BAGLANMA_BEKLEMESI_SN,
                    hata,
                )
            finally:
                self._bagli = False
            await asyncio.sleep(_YENIDEN_BAGLANMA_BEKLEMESI_SN)

    async def _mesaji_isle(self, mesaj: aiomqtt.Message) -> None:
        topic = mesaj.topic.value
        parcalar = topic.split("/")
        if len(parcalar) != 3:
            logger.warning("beklenmeyen topic düşürüldü topic=%s", topic)
            return
        _, cihaz_id, tur = parcalar

        # Sınır 1 — parse/doğrulama: bozuk mesaj akışın doğal parçasıdır, uyarıyla düşür.
        try:
            yuk = json.loads(mesaj.payload)
            if tur == "yogunluk":
                dogrulanmis: YogunlukMesaji | DurumMesaji = YogunlukMesaji.model_validate(yuk)
            elif tur == "durum":
                dogrulanmis = DurumMesaji.model_validate(yuk)
            else:
                logger.warning("bilinmeyen mesaj türü düşürüldü topic=%s", topic)
                return
        except (ValidationError, ValueError, TypeError) as hata:
            logger.warning("bozuk mesaj düşürüldü topic=%s hata=%s", topic, hata)
            return

        # Sınır 2 — işleme: beklenmeyen hata (ör. DB kopması) görevi öldüremez.
        try:
            if isinstance(dogrulanmis, YogunlukMesaji):
                await self._yogunlugu_isle(cihaz_id, dogrulanmis)
            else:
                await self._durumu_isle(cihaz_id, dogrulanmis, retained=mesaj.retain)
        except Exception:
            logger.exception("mesaj işlenirken beklenmeyen hata topic=%s", topic)

    async def _yogunlugu_isle(self, cihaz_id: str, mesaj: YogunlukMesaji) -> None:
        await self._olcum_isleyici.isle(
            cihaz_id=cihaz_id,
            sira_no=mesaj.sira_no,
            kisi_sayisi=mesaj.kisi_sayisi,
            olcum_zamani=mesaj.timestamp,
        )

    async def _durumu_isle(self, cihaz_id: str, mesaj: DurumMesaji, retained: bool) -> None:
        # Retained tekrar oynatma "şimdi görüldü" demek değildir: son_gorulme=None
        # sözleşmesi mevcut değeri korur (bkz. AnlikDurumPort).
        await self._cihaz_durum_isleyici.isle(
            cihaz_id=cihaz_id,
            cevrimici=mesaj.cevrimici,
            yazilim_surumu=mesaj.yazilim_surumu,
            son_gorulme=None if retained else datetime.now(UTC),
        )
