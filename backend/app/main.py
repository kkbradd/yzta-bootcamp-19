"""Kompozisyon kökü: somut adaptörleri kurar ve uygulamaya bağlar.

Heksagonal mimaride bağlama (wiring) yalnızca burada yapılır; use-case'ler
ve domain, altyapı kütüphanelerinden habersizdir.
"""

import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.adapters.cikan.gemini_oneri import GeminiOneriUreticisi
from app.adapters.cikan.gemini_uyari import GeminiUyariUreticisi
from app.adapters.cikan.guvenlik import BcryptSifreleyici, JwtTokenUretici
from app.adapters.cikan.postgres.baglanti import (
    motor_olustur,
    postgres_saglikli,
    tablolari_olustur,
)
from app.adapters.cikan.postgres.depolar import (
    PostgresAtamaDeposu,
    PostgresKullaniciDeposu,
    PostgresOlcumDeposu,
    PostgresOneriDeposu,
    PostgresUyariDeposu,
)
from app.adapters.cikan.postgres.sorgular import PostgresSorgular
from app.adapters.cikan.redis_baglanti import redis_istemcisi_olustur, redis_saglikli
from app.adapters.cikan.redis_durum import RedisAnlikDurum
from app.adapters.cikan.ws_yayin import BaglantiYoneticisi
from app.adapters.giren.mqtt_ingest import MqttIngest
from app.adapters.giren.oneri_zamanlayici import OneriZamanlayici
from app.adapters.giren.rest.araclar import araclar_router
from app.adapters.giren.rest.cihazlar import cihazlar_router
from app.adapters.giren.rest.hatlar import hatlar_router
from app.adapters.giren.rest.oneriler import oneriler_router
from app.adapters.giren.rest.oturum import oturum_router
from app.adapters.giren.rest.saglik import saglik_router
from app.adapters.giren.rest.tanimlar import tanimlar_router
from app.adapters.giren.rest.uyarilar import uyarilar_router
from app.adapters.giren.uyari_zamanlayici import UyariZamanlayici
from app.adapters.giren.ws import ws_router
from app.application.cihaz_durum_isle import CihazDurumIsleyici
from app.application.olcum_isle import OlcumIsleyici, SeviyeEsikleri
from app.application.oneri_uret import OneriUret
from app.application.oturum_ac import OturumAc
from app.application.uyari_uret import UyariUret
from app.ayarlar import Ayarlar


def uygulama_olustur() -> FastAPI:
    """FastAPI uygulamasını kurar; adaptörler lifespan içinde bağlanır.

    Testler gerçek adaptörler yerine `dependency_overrides` ile sahte
    kontroller enjekte eder (bkz. tests/unit/test_saglik.py).
    """

    ayarlar = Ayarlar()

    @asynccontextmanager
    async def yasam_dongusu(uygulama: FastAPI) -> AsyncIterator[None]:
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
        cihaz_durum_isleyici = CihazDurumIsleyici(anlik_durum=anlik_durum, canli_yayin=canli_yayin)
        oturum_ac = OturumAc(
            kullanici_deposu=PostgresKullaniciDeposu(oturum_fabrikasi),
            sifreleyici=BcryptSifreleyici(),
            token_uretici=JwtTokenUretici(
                gizli_anahtar=ayarlar.jwt_gizli_anahtar,
                gecerlilik_sn=ayarlar.jwt_gecerlilik_sn,
            ),
        )

        sorgular = PostgresSorgular(oturum_fabrikasi)
        oneri_deposu = PostgresOneriDeposu(oturum_fabrikasi)
        oneri_uret = OneriUret(
            sorgular=sorgular,
            oneri_uretici=GeminiOneriUreticisi(
                api_key=ayarlar.gemini_api_key, model=ayarlar.gemini_model
            ),
            oneri_deposu=oneri_deposu,
            gun_pencere=ayarlar.oneri_gun_pencere,
        )

        uyari_deposu = PostgresUyariDeposu(oturum_fabrikasi)
        uyari_uret = UyariUret(
            sorgular=sorgular,
            uyari_uretici=GeminiUyariUreticisi(
                api_key=ayarlar.gemini_api_key, model=ayarlar.gemini_model
            ),
            uyari_deposu=uyari_deposu,
            esikler=esikler,
            saat_pencere=ayarlar.uyari_saat_pencere,
        )

        # Giren adaptör: MQTT dinleyicisi arka plan görevi olarak
        ingest = MqttIngest(ayarlar, olcum_isleyici, cihaz_durum_isleyici)
        ingest_gorevi = asyncio.create_task(ingest.calistir())

        # Giren adaptör: zamanlanmış öneri üretimi arka plan görevi
        oneri_zamanlayici = OneriZamanlayici(
            oneri_uret,
            calisma_gunu=ayarlar.oneri_calisma_gunu,
            calisma_saati=ayarlar.oneri_calisma_saati,
        )
        oneri_zamanlayici_gorevi = asyncio.create_task(oneri_zamanlayici.calistir())

        # Giren adaptör: periyodik uyarı üretimi arka plan görevi
        uyari_zamanlayici = UyariZamanlayici(
            uyari_uret, periyot_sn=ayarlar.uyari_calisma_periyodu_sn
        )
        uyari_zamanlayici_gorevi = asyncio.create_task(uyari_zamanlayici.calistir())

        uygulama.state.saglik_kontrolleri = {
            "postgres": lambda: postgres_saglikli(motor),
            "redis": lambda: redis_saglikli(redis),
            "mqtt": ingest.saglikli,  # görev bağlantı durumu; istek başına bağlantı açılmaz
        }
        # REST bağımlılıkları (bkz. adapters/giren/rest/bagimliliklar.py)
        uygulama.state.esikler = esikler  # yazma ve okuma yolu aynı eşikleri paylaşır
        uygulama.state.anlik_durum = anlik_durum
        uygulama.state.sorgular = sorgular
        uygulama.state.oturum_fabrikasi = oturum_fabrikasi
        uygulama.state.ws_yonetici = canli_yayin
        uygulama.state.oturum_ac = oturum_ac
        uygulama.state.oneri_deposu = oneri_deposu
        uygulama.state.oneri_uret = oneri_uret
        uygulama.state.uyari_deposu = uyari_deposu
        uygulama.state.uyari_uret = uyari_uret
        yield

        ingest_gorevi.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await ingest_gorevi
        oneri_zamanlayici_gorevi.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await oneri_zamanlayici_gorevi
        uyari_zamanlayici_gorevi.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await uyari_zamanlayici_gorevi
        await redis.aclose()
        await motor.dispose()

    # Panel farklı origin'den (port) çağırdığında tarayıcı CORS ister.
    # İzinli origin'ler ayarlardan gelir; prod'da tek origin/proxy ise boş olabilir.
    izinli_originler = ayarlar.cors_originleri
    if "*" in izinli_originler:
        # allow_credentials=True ile joker origin tarayıcılarca reddedilir;
        # yanlış yapılandırma sessizce prod'a sızmasın diye açılışta patla.
        raise ValueError(
            "CORS_IZINLI_ORIGINLER '*' olamaz: kimlik bilgili isteklerde joker "
            "origin tarayıcılar tarafından reddedilir. Açık origin'ler belirtin."
        )
    uygulama = FastAPI(title="HAT 01 Backend", lifespan=yasam_dongusu)
    uygulama.add_middleware(
        CORSMiddleware,
        allow_origins=izinli_originler,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uygulama.include_router(saglik_router)
    uygulama.include_router(hatlar_router)
    uygulama.include_router(araclar_router)
    uygulama.include_router(cihazlar_router)
    uygulama.include_router(tanimlar_router)
    uygulama.include_router(oturum_router)
    uygulama.include_router(oneriler_router)
    uygulama.include_router(uyarilar_router)
    uygulama.include_router(ws_router)
    return uygulama


uygulama = uygulama_olustur()
