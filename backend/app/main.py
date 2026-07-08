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

from app.adapters.cikan.bellek_ici import BellekIciAnlikDurum, SessizYayin
from app.adapters.cikan.postgres.baglanti import (
    motor_olustur,
    postgres_saglikli,
    tablolari_olustur,
)
from app.adapters.cikan.postgres.depolar import PostgresAtamaDeposu, PostgresOlcumDeposu
from app.adapters.cikan.redis_baglanti import redis_istemcisi_olustur, redis_saglikli
from app.adapters.giren.mqtt_ingest import MqttIngest
from app.adapters.giren.rest.saglik import saglik_router
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
        anlik_durum = BellekIciAnlikDurum()  # Faz 3'te Redis implementasyonuyla değişecek
        canli_yayin = SessizYayin()  # Faz 4'te WebSocket implementasyonuyla değişecek

        # Use-case'ler
        olcum_isleyici = OlcumIsleyici(
            olcum_deposu=PostgresOlcumDeposu(oturum_fabrikasi),
            atama_deposu=PostgresAtamaDeposu(oturum_fabrikasi),
            anlik_durum=anlik_durum,
            canli_yayin=canli_yayin,
            esikler=SeviyeEsikleri(
                seyrek_ust=ayarlar.seviye_seyrek_ust, orta_ust=ayarlar.seviye_orta_ust
            ),
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
        yield

        ingest_gorevi.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await ingest_gorevi
        await redis.aclose()
        await motor.dispose()

    uygulama = FastAPI(title="HAT 01 Backend", lifespan=yasam_dongusu)
    uygulama.include_router(saglik_router)
    return uygulama


uygulama = uygulama_olustur()
