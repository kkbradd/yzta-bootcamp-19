"""REST router'larının bağımlılık sağlayıcıları.

Somut adaptörler lifespan'da app.state'e konur (bkz. main.py); testler bu
sağlayıcıları dependency_overrides ile sahteleriyle değiştirir.
"""

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.cikan.postgres.sorgular import PostgresSorgular
from app.adapters.cikan.redis_durum import RedisAnlikDurum
from app.application.olcum_isle import SeviyeEsikleri
from app.application.oturum_ac import OturumAc


def anlik_durumu_getir(istek: Request) -> RedisAnlikDurum:
    return istek.app.state.anlik_durum


def sorgulari_getir(istek: Request) -> PostgresSorgular:
    return istek.app.state.sorgular


def esikleri_getir(istek: Request) -> SeviyeEsikleri:
    return istek.app.state.esikler


def oturum_fabrikasini_getir(istek: Request) -> async_sessionmaker[AsyncSession]:
    return istek.app.state.oturum_fabrikasi


def oturum_ac_use_case_getir(istek: Request) -> OturumAc:
    return istek.app.state.oturum_ac
