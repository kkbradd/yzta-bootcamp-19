"""Sağlık ucu: servis ve bağımlılıklarının (PostgreSQL, Redis, MQTT) durumunu raporlar."""

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

SaglikKontrolu = Callable[[], Awaitable[bool]]

saglik_router = APIRouter(prefix="/api")


def saglik_kontrollerini_getir(istek: Request) -> Mapping[str, SaglikKontrolu]:
    return istek.app.state.saglik_kontrolleri


@saglik_router.get("/saglik")
async def saglik(
    kontroller: Annotated[Mapping[str, SaglikKontrolu], Depends(saglik_kontrollerini_getir)],
) -> JSONResponse:
    # Bağımsız kontroller — sırayla beklemek yerine eşzamanlı çalıştırılır.
    sonuclar = await asyncio.gather(*(_guvenli_kontrol(k) for k in kontroller.values()))
    bagimliliklar = {
        ad: "ok" if saglikli else "hata"
        for ad, saglikli in zip(kontroller, sonuclar, strict=True)
    }
    hepsi_saglikli = all(sonuclar)
    return JSONResponse(
        content={"durum": "ok" if hepsi_saglikli else "hata", "bagimliliklar": bagimliliklar},
        status_code=200 if hepsi_saglikli else 503,
    )


async def _guvenli_kontrol(kontrol: SaglikKontrolu) -> bool:
    """Sağlık ucu hiçbir bağımlılık istisnasında düşmemeli; istisna = sağlıksız."""
    try:
        return await kontrol()
    except Exception:  # noqa: BLE001
        return False
