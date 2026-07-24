"""Durak uçları: tüm duraklar listesi (koordinatlı, harita için)."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapters.cikan.postgres.sorgular import PostgresSorgular
from app.adapters.giren.rest.bagimliliklar import sorgulari_getir
from app.adapters.giren.rest.semalar import DurakYaniti

duraklar_router = APIRouter(prefix="/api/duraklar")

Sorgular = Annotated[PostgresSorgular, Depends(sorgulari_getir)]


@duraklar_router.get("")
async def duraklari_listele(sorgular: Sorgular) -> list[DurakYaniti]:
    duraklar = await sorgular.duraklari_listele()
    hat_kodlari = await sorgular.durak_hat_kodlarini_listele()
    return [
        DurakYaniti(
            id=d.id, ad=d.ad, enlem=d.enlem, boylam=d.boylam,
            hat_kodlari=hat_kodlari.get(d.id, []),
        )
        for d in duraklar
    ]
