"""Giriş ucu: eposta + şifreyi doğrular, başarılıysa JWT döner."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.adapters.giren.rest.bagimliliklar import oturum_ac_use_case_getir
from app.adapters.giren.rest.semalar import OturumAcIstegi, OturumYaniti
from app.application.oturum_ac import OturumAc

oturum_router = APIRouter(prefix="/api")

OturumAcUseCase = Annotated[OturumAc, Depends(oturum_ac_use_case_getir)]


@oturum_router.post("/oturum")
async def oturum_ac(istek: OturumAcIstegi, use_case: OturumAcUseCase) -> OturumYaniti:
    token = await use_case.calistir(istek.eposta, istek.sifre)
    if token is None:
        raise HTTPException(status_code=401, detail="e-posta veya şifre hatalı")
    return OturumYaniti(erisim_tokeni=token)
