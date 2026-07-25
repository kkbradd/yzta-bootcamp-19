"""Uyarı uçları: listeleme + manuel tetikleme (geliştirici/demo kolaylığı)."""

import dataclasses
from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapters.giren.rest.bagimliliklar import uyari_deposu_getir, uyari_uret_getir
from app.adapters.giren.rest.semalar import UyariYaniti
from app.application.uyari_uret import UyariUret
from app.ports.uyari import UyariDeposuPort

uyarilar_router = APIRouter(prefix="/api/uyarilar")

UyariDeposu = Annotated[UyariDeposuPort, Depends(uyari_deposu_getir)]
UyariUretUseCase = Annotated[UyariUret, Depends(uyari_uret_getir)]


@uyarilar_router.get("")
async def uyarilari_listele(depo: UyariDeposu, limit: int = 50) -> list[UyariYaniti]:
    uyarilar = await depo.son_uyarilar(limit)
    return [UyariYaniti(**dataclasses.asdict(u)) for u in uyarilar]


@uyarilar_router.post("/uret", status_code=202)
async def uyari_uret_tetikle(use_case: UyariUretUseCase) -> list[UyariYaniti]:
    """Geliştirici/demo amaçlı: zamanlamayı beklemeden manuel tetikler."""
    uyarilar = await use_case.calistir()
    return [UyariYaniti(**dataclasses.asdict(u)) for u in uyarilar]
