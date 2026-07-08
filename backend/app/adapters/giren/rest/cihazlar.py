"""Cihaz uçları: liste + çevrimiçi durumu (PG + Redis) — plan Bölüm 9."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapters.cikan.postgres.sorgular import PostgresSorgular
from app.adapters.cikan.redis_durum import RedisAnlikDurum
from app.adapters.giren.rest.bagimliliklar import anlik_durumu_getir, sorgulari_getir
from app.adapters.giren.rest.semalar import CihazYaniti

cihazlar_router = APIRouter(prefix="/api/cihazlar")


@cihazlar_router.get("")
async def cihazlari_listele(
    sorgular: Annotated[PostgresSorgular, Depends(sorgulari_getir)],
    anlik: Annotated[RedisAnlikDurum, Depends(anlik_durumu_getir)],
) -> list[CihazYaniti]:
    yanitlar = []
    for cihaz in await sorgular.cihazlari_listele():
        durum = await anlik.cihaz_durumu(cihaz.id)
        yanitlar.append(
            CihazYaniti(
                id=cihaz.id,
                tip=cihaz.tip,
                # Cihazın bildirdiği güncel sürüm tercih edilir; yoksa kayıt değeri.
                yazilim_surumu=(
                    durum.yazilim_surumu if durum and durum.yazilim_surumu else cihaz.yazilim_surumu
                ),
                cevrimici=durum.cevrimici if durum else False,
                son_gorulme=durum.son_gorulme if durum else None,
            )
        )
    return yanitlar
