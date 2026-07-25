"""HTTP servisi — POST /chat ile asistana soru sorulur.

Asistan, lifespan içinde bir kez kurulur; testler ``uygulama_olustur``'a
sahte asistan üreten bir fabrika vererek modeli/ağı devre dışı bırakır.
"""

import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from app.ayarlar import SECILEBILIR_MODEL_ADLARI, SECILEBILIR_MODELLER, Ayarlar
from app.cekirdek import Soran, YotayAsistani
from app.model_hazirla import CEKME_ZAMAN_ASIMI_SN, mevcut_modeller, model_indir

logger = logging.getLogger("asistan.servis")


class SohbetIstegi(BaseModel):
    mesaj: str = Field(min_length=1)
    # Seçilebilir modellerden biri; boş bırakılırsa servisin varsayılanı kullanılır.
    model: str | None = None


class SohbetYaniti(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cevap: str
    tur_sayisi: int
    arac_cagrilari: list[str]
    model: str = ""


class ModelBilgisi(BaseModel):
    ad: str
    etiket: str
    boyut: str
    indirildi_mi: bool
    varsayilan_mi: bool


class IndirmeIstegi(BaseModel):
    model: str


def _varsayilan_asistan() -> YotayAsistani:
    return YotayAsistani.ayarlardan(Ayarlar.ortamdan())


def uygulama_olustur(
    asistan_fabrikasi: Callable[[], Soran] = _varsayilan_asistan,
    ayarlar: Ayarlar | None = None,
) -> FastAPI:
    izinli_originler = (ayarlar or Ayarlar.ortamdan()).cors_originleri

    cozulmus_ayarlar = ayarlar or Ayarlar.ortamdan()

    @asynccontextmanager
    async def yasam_dongusu(uygulama: FastAPI) -> AsyncIterator[None]:
        uygulama.state.asistan = asistan_fabrikasi()
        uygulama.state.ayarlar = cozulmus_ayarlar
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
    uygulama.get("/modeller")(_modelleri_listele)
    uygulama.post("/modeller/indir")(_modeli_indir)
    uygulama.get("/saglik")(_saglik)
    return uygulama


def _modeli_dogrula(model: str | None) -> str | None:
    """Serbest model adı kabul edilmez: keyfi `/api/pull` tetiklenmesini önler."""
    if model is None or not model.strip():
        return None
    if model not in SECILEBILIR_MODEL_ADLARI:
        raise HTTPException(
            status_code=400,
            detail=f"'{model}' seçilebilir modellerden değil: {', '.join(SECILEBILIR_MODEL_ADLARI)}",
        )
    return model


def _sohbet(istek: SohbetIstegi, request: Request) -> SohbetYaniti:
    model = _modeli_dogrula(istek.model)
    cevap = request.app.state.asistan.sor(istek.mesaj, model=model)
    return SohbetYaniti.model_validate(cevap)


def _ollama_istemcisi(request: Request, zaman_asimi_sn: float = 30.0) -> httpx.Client:
    ayarlar: Ayarlar = request.app.state.ayarlar
    return httpx.Client(base_url=ayarlar.ollama_adresi, timeout=zaman_asimi_sn)


def _modelleri_listele(request: Request) -> list[ModelBilgisi]:
    ayarlar: Ayarlar = request.app.state.ayarlar
    try:
        with _ollama_istemcisi(request) as istemci:
            indirilenler = set(mevcut_modeller(istemci))
    except httpx.HTTPError as hata:
        # Ollama'ya ulaşılamıyorsa liste yine dönsün; ekran "indirilmedi" gösterir
        # ve kullanıcı boş sayfa yerine ne olduğunu görür.
        logger.warning("Ollama model listesi alınamadı: %s", hata)
        indirilenler = set()

    return [
        ModelBilgisi(
            ad=model["ad"],
            etiket=model["etiket"],
            boyut=model["boyut"],
            indirildi_mi=model["ad"] in indirilenler,
            varsayilan_mi=model["ad"] == ayarlar.model,
        )
        for model in SECILEBILIR_MODELLER
    ]


def _modeli_indir(istek: IndirmeIstegi, request: Request) -> ModelBilgisi:
    model = _modeli_dogrula(istek.model)
    if model is None:
        raise HTTPException(status_code=400, detail="model alanı zorunlu.")

    ayarlar: Ayarlar = request.app.state.ayarlar
    try:
        # İndirme GB'larca sürebilir; model_hazirla'nın uzun zaman aşımı kullanılır.
        with _ollama_istemcisi(request, zaman_asimi_sn=CEKME_ZAMAN_ASIMI_SN) as istemci:
            model_indir(model, istemci)
    except httpx.HTTPError as hata:
        raise HTTPException(status_code=502, detail=f"Model indirilemedi: {hata}") from hata

    tanim = next(m for m in SECILEBILIR_MODELLER if m["ad"] == model)
    return ModelBilgisi(
        ad=model,
        etiket=tanim["etiket"],
        boyut=tanim["boyut"],
        indirildi_mi=True,
        varsayilan_mi=model == ayarlar.model,
    )


def _saglik() -> dict[str, str]:
    return {"durum": "calisiyor"}


uygulama = uygulama_olustur()
