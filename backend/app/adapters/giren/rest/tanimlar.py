"""Tanımlar ekranı: minimal CRUD uçları (plan Bölüm 9).

İş kuralı içermez; plan Bölüm 4 pragmatizmi gereği port katmanı olmadan,
ince router + doğrudan PostgreSQL ile yazılmıştır. Tek istisna atama
oluşturma: aynı hedefin açık ataması varsa kapatılır — aksi halde
"güncel atama = bitis IS NULL" değişmezi bozulurdu.
"""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.cikan.postgres.tablolar import (
    AracTablosu,
    CihazAtamasiTablosu,
    CihazTablosu,
    DurakTablosu,
    HatAtamasiTablosu,
    HatTablosu,
    Taban,
)
from app.adapters.giren.rest.bagimliliklar import oturum_fabrikasini_getir
from app.adapters.giren.rest.semalar import (
    AracOlustur,
    AtamaOlustur,
    CihazAtamasiOlustur,
    CihazOlustur,
    DurakOlustur,
    HatOlustur,
)

tanimlar_router = APIRouter(prefix="/api")

OturumFabrikasi = Annotated[async_sessionmaker[AsyncSession], Depends(oturum_fabrikasini_getir)]


async def _kaydet(oturum_fabrikasi: async_sessionmaker[AsyncSession], satir: Taban) -> dict:
    """Tek satırı kalıcılaştırır; kısıt ihlalini (mükerrer/eksik FK) 409'a çevirir."""
    try:
        async with oturum_fabrikasi() as oturum:
            oturum.add(satir)
            await oturum.commit()
            return {"id": satir.id}
    except IntegrityError as hata:
        raise HTTPException(
            status_code=409, detail="kayıt çakışması veya geçersiz referans"
        ) from hata


@tanimlar_router.post("/hatlar", status_code=201)
async def hat_olustur(istek: HatOlustur, oturum_fabrikasi: OturumFabrikasi) -> dict:
    return await _kaydet(oturum_fabrikasi, HatTablosu(hat_no=istek.hat_no, ad=istek.ad))


@tanimlar_router.post("/araclar", status_code=201)
async def arac_olustur(istek: AracOlustur, oturum_fabrikasi: OturumFabrikasi) -> dict:
    return await _kaydet(
        oturum_fabrikasi, AracTablosu(plaka=istek.plaka, tip=istek.tip, kapasite=istek.kapasite)
    )


@tanimlar_router.post("/duraklar", status_code=201)
async def durak_olustur(istek: DurakOlustur, oturum_fabrikasi: OturumFabrikasi) -> dict:
    return await _kaydet(
        oturum_fabrikasi, DurakTablosu(ad=istek.ad, enlem=istek.enlem, boylam=istek.boylam)
    )


@tanimlar_router.post("/cihazlar", status_code=201)
async def cihaz_olustur(istek: CihazOlustur, oturum_fabrikasi: OturumFabrikasi) -> dict:
    return await _kaydet(
        oturum_fabrikasi,
        CihazTablosu(id=istek.id, tip=istek.tip, yazilim_surumu=istek.yazilim_surumu),
    )


@tanimlar_router.post("/atamalar", status_code=201)
async def atama_olustur(istek: AtamaOlustur, oturum_fabrikasi: OturumFabrikasi) -> dict:
    simdi = datetime.now(UTC)
    try:
        return await _atamayi_kaydet(oturum_fabrikasi, istek, simdi)
    except IntegrityError as hata:
        raise HTTPException(
            status_code=409, detail="geçersiz referans (hat/araç/cihaz/durak)"
        ) from hata


async def _atamayi_kaydet(
    oturum_fabrikasi: async_sessionmaker[AsyncSession], istek: AtamaOlustur, simdi: datetime
) -> dict:
    async with oturum_fabrikasi() as oturum:
        if isinstance(istek, CihazAtamasiOlustur):
            # Aynı cihazın açık atamasını kapat (güncel atama tekilliği).
            await oturum.execute(
                update(CihazAtamasiTablosu)
                .where(
                    CihazAtamasiTablosu.cihaz_id == istek.cihaz_id,
                    CihazAtamasiTablosu.bitis.is_(None),
                )
                .values(bitis=simdi)
            )
            satir: CihazAtamasiTablosu | HatAtamasiTablosu = CihazAtamasiTablosu(
                cihaz_id=istek.cihaz_id,
                arac_id=istek.arac_id,
                durak_id=istek.durak_id,
                baslangic=simdi,
            )
        else:
            # Aynı aracın açık hat atamasını kapat.
            await oturum.execute(
                update(HatAtamasiTablosu)
                .where(
                    HatAtamasiTablosu.arac_id == istek.arac_id,
                    HatAtamasiTablosu.bitis.is_(None),
                )
                .values(bitis=simdi)
            )
            satir = HatAtamasiTablosu(hat_id=istek.hat_id, arac_id=istek.arac_id, baslangic=simdi)
        oturum.add(satir)
        await oturum.commit()
        return {"id": satir.id}
