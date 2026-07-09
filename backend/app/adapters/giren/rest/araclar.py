"""Araç uçları: tek aracın tarihsel ölçümleri (PostgreSQL) — plan Bölüm 9."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapters.cikan.postgres.sorgular import PostgresSorgular
from app.adapters.giren.rest.bagimliliklar import sorgulari_getir
from app.adapters.giren.rest.semalar import OlcumYaniti

araclar_router = APIRouter(prefix="/api/araclar")


@araclar_router.get("/{arac_id}/olcumler")
async def arac_olcumleri(
    arac_id: int,
    baslangic: datetime,
    bitis: datetime,
    sorgular: Annotated[PostgresSorgular, Depends(sorgulari_getir)],
) -> list[OlcumYaniti]:
    olcumler = await sorgular.arac_olcumleri(arac_id, baslangic, bitis)
    return [
        OlcumYaniti(
            sira_no=o.sira_no,
            kisi_sayisi=o.kisi_sayisi,
            doluluk_orani=o.doluluk_orani,
            seviye=o.seviye,
            olcum_zamani=o.olcum_zamani,
        )
        for o in olcumler
    ]
