"""Öneri uçları: listeleme + manuel tetikleme (geliştirici/demo kolaylığı)."""

import dataclasses
from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapters.giren.rest.bagimliliklar import oneri_deposu_getir, oneri_uret_getir
from app.adapters.giren.rest.semalar import OneriYaniti
from app.application.oneri_uret import OneriUret
from app.ports.oneri import OneriDeposuPort

oneriler_router = APIRouter(prefix="/api/oneriler")

OneriDeposu = Annotated[OneriDeposuPort, Depends(oneri_deposu_getir)]
OneriUretUseCase = Annotated[OneriUret, Depends(oneri_uret_getir)]


@oneriler_router.get("")
async def oneleri_listele(depo: OneriDeposu, limit: int = 50) -> list[OneriYaniti]:
    oneriler = await depo.son_oneriler(limit)
    return [OneriYaniti(**dataclasses.asdict(o)) for o in oneriler]


@oneriler_router.post("/uret", status_code=202)
async def oneri_uret_tetikle(use_case: OneriUretUseCase) -> list[OneriYaniti]:
    """Geliştirici/demo amaçlı: zamanlamayı beklemeden manuel tetikler."""
    oneriler = await use_case.calistir()
    return [OneriYaniti(**dataclasses.asdict(o)) for o in oneriler]
