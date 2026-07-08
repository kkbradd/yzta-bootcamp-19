"""Kompozisyon kökü: somut adaptörleri kurar ve uygulamaya bağlar.

Heksagonal mimaride bağlama (wiring) yalnızca burada yapılır; use-case'ler
ve domain, altyapı kütüphanelerinden habersizdir.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.adapters.cikan.postgres.baglanti import (
    motor_olustur,
    postgres_saglikli,
    tablolari_olustur,
)
from app.adapters.cikan.redis_baglanti import redis_istemcisi_olustur, redis_saglikli
from app.adapters.giren.mqtt_ingest import mqtt_saglikli
from app.adapters.giren.rest.saglik import saglik_router
from app.ayarlar import Ayarlar


def uygulama_olustur() -> FastAPI:
    """FastAPI uygulamasını kurar; adaptörler lifespan içinde bağlanır.

    Testler gerçek adaptörler yerine `dependency_overrides` ile sahte
    kontroller enjekte eder (bkz. tests/unit/test_saglik.py).
    """

    @asynccontextmanager
    async def yasam_dongusu(uygulama: FastAPI) -> AsyncIterator[None]:
        ayarlar = Ayarlar()
        motor = motor_olustur(ayarlar.database_url)
        await tablolari_olustur(motor)
        redis = redis_istemcisi_olustur(ayarlar.redis_url)
        uygulama.state.saglik_kontrolleri = {
            "postgres": lambda: postgres_saglikli(motor),
            "redis": lambda: redis_saglikli(redis),
            "mqtt": lambda: mqtt_saglikli(ayarlar),
        }
        yield
        await redis.aclose()
        await motor.dispose()

    uygulama = FastAPI(title="HAT 01 Backend", lifespan=yasam_dongusu)
    uygulama.include_router(saglik_router)
    return uygulama


uygulama = uygulama_olustur()
