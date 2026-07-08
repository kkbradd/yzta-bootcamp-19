"""Kompozisyon kökü: somut adaptörleri kurar ve uygulamaya bağlar.

Heksagonal mimaride bağlama (wiring) yalnızca burada yapılır; use-case'ler
ve domain, altyapı kütüphanelerinden habersizdir.
"""

import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.adapters.cikan.postgres.baglanti import (
    motor_olustur,
    postgres_saglikli,
    tablolari_olustur,
)
from app.adapters.cikan.postgres.depolar import PostgresAtamaDeposu, PostgresOlcumDeposu
from app.adapters.cikan.postgres.sorgular import PostgresSorgular
from app.adapters.cikan.redis_baglanti import redis_istemcisi_olustur, redis_saglikli
from app.adapters.cikan.redis_durum import RedisAnlikDurum
from app.adapters.cikan.ws_yayin import BaglantiYoneticisi
from app.adapters.giren.mqtt_ingest import MqttIngest
from app.adapters.giren.rest.araclar import araclar_router
from app.adapters.giren.rest.cihazlar import cihazlar_router
from app.adapters.giren.rest.hatlar import hatlar_router
from app.adapters.giren.rest.saglik import saglik_router
from app.adapters.giren.rest.tanimlar import tanimlar_router
from app.adapters.giren.ws import ws_router
from app.application.cihaz_durum_isle import CihazDurumIsleyici
from app.application.olcum_isle import OlcumIsleyici, SeviyeEsikleri
from app.ayarlar import Ayarlar


def uygulama_olustur() -> FastAPI:
    """FastAPI uygulamasını kurar; adaptörler lifespan içinde bağlanır.

    Testler gerçek adaptörler yerine `dependency_overrides` ile sahte
    kontroller enjekte eder (bkz. tests/unit/test_saglik.py).
    """

    @asynccontextmanager
    async def yasam_dongusu(uygulama: FastAPI) -> AsyncIterator[None]:
        ayarlar = Ayarlar()

        # Çıkan adaptörler
        motor = motor_olustur(ayarlar.database_url)
        await tablolari_olustur(motor)
        oturum_fabrikasi = async_sessionmaker(motor, expire_on_commit=False)
        redis = redis_istemcisi_olustur(ayarlar.redis_url)
        anlik_durum = RedisAnlikDurum(
            redis, arac_ttl_sn=ayarlar.redis_arac_ttl_sn, hat_ttl_sn=ayarlar.redis_hat_ttl_sn
        )
        canli_yayin = BaglantiYoneticisi()

        # Use-case'ler
        esikler = SeviyeEsikleri(
            seyrek_ust=ayarlar.seviye_seyrek_ust, orta_ust=ayarlar.seviye_orta_ust
        )
        olcum_isleyici = OlcumIsleyici(
            olcum_deposu=PostgresOlcumDeposu(oturum_fabrikasi),
            atama_deposu=PostgresAtamaDeposu(oturum_fabrikasi),
            anlik_durum=anlik_durum,
            canli_yayin=canli_yayin,
            esikler=esikler,
        )
        cihaz_durum_isleyici = CihazDurumIsleyici(
            anlik_durum=anlik_durum, canli_yayin=canli_yayin
        )

        # Giren adaptör: MQTT dinleyicisi arka plan görevi olarak
        ingest = MqttIngest(ayarlar, olcum_isleyici, cihaz_durum_isleyici)
        ingest_gorevi = asyncio.create_task(ingest.calistir())

        uygulama.state.saglik_kontrolleri = {
            "postgres": lambda: postgres_saglikli(motor),
            "redis": lambda: redis_saglikli(redis),
            "mqtt": ingest.saglikli,  # görev bağlantı durumu; istek başına bağlantı açılmaz
        }
        # REST bağımlılıkları (bkz. adapters/giren/rest/bagimliliklar.py)
        uygulama.state.esikler = esikler  # yazma ve okuma yolu aynı eşikleri paylaşır
        uygulama.state.anlik_durum = anlik_durum
        uygulama.state.sorgular = PostgresSorgular(oturum_fabrikasi)
        uygulama.state.oturum_fabrikasi = oturum_fabrikasi
        uygulama.state.ws_yonetici = canli_yayin
        yield

        ingest_gorevi.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await ingest_gorevi
        await redis.aclose()
        await motor.dispose()

    uygulama = FastAPI(title="HAT 01 Backend", lifespan=yasam_dongusu)
    uygulama.include_router(saglik_router)
    uygulama.include_router(hatlar_router)
    uygulama.include_router(araclar_router)
    uygulama.include_router(cihazlar_router)
    uygulama.include_router(tanimlar_router)
    uygulama.include_router(ws_router)
    return uygulama


uygulama = uygulama_olustur()
