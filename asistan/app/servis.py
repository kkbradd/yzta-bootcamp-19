"""HTTP servisi — POST /chat ile asistana soru sorulur.

Asistan, lifespan içinde bir kez kurulur; testler ``uygulama_olustur``'a
sahte asistan üreten bir fabrika vererek modeli/ağı devre dışı bırakır.
"""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from app.ayarlar import Ayarlar
from app.cekirdek import Soran, YotayAsistani


class SohbetIstegi(BaseModel):
    mesaj: str = Field(min_length=1)


class SohbetYaniti(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cevap: str
    tur_sayisi: int
    arac_cagrilari: list[str]


def _varsayilan_asistan() -> YotayAsistani:
    return YotayAsistani.ayarlardan(Ayarlar.ortamdan())


def uygulama_olustur(
    asistan_fabrikasi: Callable[[], Soran] = _varsayilan_asistan,
    ayarlar: Ayarlar | None = None,
) -> FastAPI:
    izinli_originler = (ayarlar or Ayarlar.ortamdan()).cors_originleri

    @asynccontextmanager
    async def yasam_dongusu(uygulama: FastAPI) -> AsyncIterator[None]:
        uygulama.state.asistan = asistan_fabrikasi()
        yield

    uygulama = FastAPI(title="YOTAY Asistan", lifespan=yasam_dongusu)
    # Panel ayrı port'ta (3000) çalıştığı için tarayıcı CORS ister; izinli origin'ler
    # ayarlardan gelir ve '*' açılışta reddedilir (bkz. Ayarlar._corsu_dogrula).
    uygulama.add_middleware(
        CORSMiddleware,
        allow_origins=izinli_originler,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uygulama.post("/chat")(_sohbet)
    uygulama.get("/saglik")(_saglik)
    return uygulama


def _sohbet(istek: SohbetIstegi, request: Request) -> SohbetYaniti:
    cevap = request.app.state.asistan.sor(istek.mesaj)
    return SohbetYaniti.model_validate(cevap)


def _saglik() -> dict[str, str]:
    return {"durum": "calisiyor"}


uygulama = uygulama_olustur()
