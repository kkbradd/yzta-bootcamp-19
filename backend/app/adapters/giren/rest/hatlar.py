"""Hat uçları: anlık özet (Redis) ve tarihsel trend (PostgreSQL) — plan Bölüm 9."""

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends

from app.adapters.cikan.postgres.sorgular import PostgresSorgular
from app.adapters.cikan.redis_durum import RedisAnlikDurum
from app.adapters.giren.rest.bagimliliklar import (
    anlik_durumu_getir,
    esikleri_getir,
    sorgulari_getir,
)
from app.adapters.giren.rest.semalar import (
    AracAnlikDurumu,
    DurakYaniti,
    HatGuzergahYaniti,
    HatOzeti,
    TrendNoktasi,
)
from app.application.olcum_isle import SeviyeEsikleri
from app.domain.seviye import seviye_belirle

hatlar_router = APIRouter(prefix="/api/hatlar")

AnlikDurum = Annotated[RedisAnlikDurum, Depends(anlik_durumu_getir)]
Sorgular = Annotated[PostgresSorgular, Depends(sorgulari_getir)]
Esikler = Annotated[SeviyeEsikleri, Depends(esikleri_getir)]


@hatlar_router.get("")
async def hatlari_listele(
    anlik: AnlikDurum, sorgular: Sorgular, esikler: Esikler
) -> list[HatOzeti]:
    ozetler = []
    for hat in await sorgular.hatlari_listele():
        ortalama, arac_sayisi = await anlik.hat_ozeti(hat.id)
        ozetler.append(
            HatOzeti(
                hat_id=hat.id,
                hat_no=hat.hat_no,
                ad=hat.ad,
                ortalama_doluluk=ortalama,
                seviye=(
                    seviye_belirle(ortalama, esikler.seyrek_ust, esikler.orta_ust)
                    if ortalama is not None
                    else None
                ),
                arac_sayisi=arac_sayisi,
            )
        )
    return ozetler


@hatlar_router.get("/{hat_id}/anlik")
async def hat_anlik_durumu(hat_id: int, anlik: AnlikDurum) -> list[AracAnlikDurumu]:
    durumlar = []
    for arac_id in await anlik.hat_arac_doluluklari(hat_id):
        durum = await anlik.arac_durumu(arac_id)
        if durum is None:  # araç anahtarı TTL ile düşmüş olabilir
            continue
        durumlar.append(
            AracAnlikDurumu(
                arac_id=arac_id,
                kisi_sayisi=durum.kisi_sayisi,
                doluluk_orani=durum.doluluk_orani,
                seviye=durum.seviye,
                zaman=durum.zaman,
            )
        )
    return durumlar


@hatlar_router.get("/{hat_id}/guzergah")
async def hat_guzergahi(hat_id: int, sorgular: Sorgular) -> HatGuzergahYaniti:
    duraklar = await sorgular.hat_duraklarini_listele(hat_id)
    guzergah = await sorgular.hat_guzergahini_getir(hat_id)
    return HatGuzergahYaniti(
        duraklar=[
            DurakYaniti(id=d.id, ad=d.ad, enlem=d.enlem, boylam=d.boylam) for d in duraklar
        ],
        koordinatlar=guzergah.koordinatlar if guzergah else [],
        mesafe_metre=guzergah.mesafe_metre if guzergah else None,
        sure_saniye=guzergah.sure_saniye if guzergah else None,
    )


@hatlar_router.get("/{hat_id}/trend")
async def hat_trendi(
    hat_id: int,
    baslangic: datetime,
    bitis: datetime,
    sorgular: Sorgular,
    aralik: Literal["saat", "15dk"] = "saat",
) -> list[TrendNoktasi]:
    noktalar = await sorgular.hat_trendi(hat_id, baslangic, bitis, aralik)
    return [TrendNoktasi(**nokta) for nokta in noktalar]
