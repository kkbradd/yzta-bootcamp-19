"""REST router'larının bağımlılık sağlayıcıları.

Somut adaptörler lifespan'da app.state'e konur (bkz. main.py); testler bu
sağlayıcıları dependency_overrides ile sahteleriyle değiştirir.
"""

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.cikan.postgres.sorgular import PostgresSorgular
from app.adapters.cikan.redis_durum import RedisAnlikDurum
from app.application.olcum_isle import SeviyeEsikleri
from app.application.oneri_uret import OneriUret
from app.application.oturum_ac import OturumAc
from app.application.uyari_uret import UyariUret
from app.ports.oneri import OneriDeposuPort
from app.ports.uyari import UyariDeposuPort


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


def oneri_deposu_getir(istek: Request) -> OneriDeposuPort:
    return istek.app.state.oneri_deposu


def oneri_uret_getir(istek: Request) -> OneriUret:
    return istek.app.state.oneri_uret


def uyari_deposu_getir(istek: Request) -> UyariDeposuPort:
    return istek.app.state.uyari_deposu


def uyari_uret_getir(istek: Request) -> UyariUret:
    return istek.app.state.uyari_uret
