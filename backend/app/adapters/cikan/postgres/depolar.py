"""Depo portlarının PostgreSQL implementasyonları.

Adaptör, domain nesnesi ↔ tablo satırı çevirisini kendisi yapar;
yukarı katmanlara SQLAlchemy tipi sızmaz.
"""

from datetime import datetime

from sqlalchemy import ColumnElement, and_, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.cikan.postgres.tablolar import (
    AracTablosu,
    CihazAtamasiTablosu,
    HatAtamasiTablosu,
    OlcumTablosu,
)
from app.domain.modeller import Arac, CihazAtamasi, HatAtamasi, Olcum

OturumFabrikasi = async_sessionmaker[AsyncSession]


class PostgresOlcumDeposu:
    """OlcumDeposuPort implementasyonu — dedup UNIQUE + ON CONFLICT ile veritabanında."""

    def __init__(self, oturum_fabrikasi: OturumFabrikasi) -> None:
        self._oturum_fabrikasi = oturum_fabrikasi

    async def ekle(self, olcum: Olcum) -> bool:
        ifade = (
            pg_insert(OlcumTablosu)
            .values(
                cihaz_id=olcum.cihaz_id,
                arac_id=olcum.arac_id,
                hat_id=olcum.hat_id,
                sira_no=olcum.sira_no,
                kisi_sayisi=olcum.kisi_sayisi,
                doluluk_orani=olcum.doluluk_orani,
                seviye=olcum.seviye,
                olcum_zamani=olcum.olcum_zamani,
            )
            .on_conflict_do_nothing(constraint="uq_olcumler_cihaz_sira")
        )
        async with self._oturum_fabrikasi() as oturum:
            sonuc = await oturum.execute(ifade)
            await oturum.commit()
        return sonuc.rowcount == 1


def _o_anda_gecerli(
    baslangic: ColumnElement[datetime], bitis: ColumnElement[datetime | None], an: datetime
) -> ColumnElement[bool]:
    """Zaman aralıklı atama tablolarında as-of koşulu (güncel kayıt: bitis IS NULL)."""
    return and_(baslangic <= an, or_(bitis.is_(None), bitis > an))


class PostgresAtamaDeposu:
    """AtamaDeposuPort implementasyonu — atamalar çekim anına göre çözülür."""

    def __init__(self, oturum_fabrikasi: OturumFabrikasi) -> None:
        self._oturum_fabrikasi = oturum_fabrikasi

    async def cihaz_atamasini_bul(self, cihaz_id: str, an: datetime) -> CihazAtamasi | None:
        ifade = select(CihazAtamasiTablosu).where(
            CihazAtamasiTablosu.cihaz_id == cihaz_id,
            _o_anda_gecerli(CihazAtamasiTablosu.baslangic, CihazAtamasiTablosu.bitis, an),
        )
        async with self._oturum_fabrikasi() as oturum:
            satir = await oturum.scalar(ifade)
        if satir is None:
            return None
        return CihazAtamasi(
            id=satir.id,
            cihaz_id=satir.cihaz_id,
            baslangic=satir.baslangic,
            arac_id=satir.arac_id,
            durak_id=satir.durak_id,
            bitis=satir.bitis,
        )

    async def hat_atamasini_bul(self, arac_id: int, an: datetime) -> HatAtamasi | None:
        ifade = select(HatAtamasiTablosu).where(
            HatAtamasiTablosu.arac_id == arac_id,
            _o_anda_gecerli(HatAtamasiTablosu.baslangic, HatAtamasiTablosu.bitis, an),
        )
        async with self._oturum_fabrikasi() as oturum:
            satir = await oturum.scalar(ifade)
        if satir is None:
            return None
        return HatAtamasi(
            id=satir.id,
            hat_id=satir.hat_id,
            arac_id=satir.arac_id,
            baslangic=satir.baslangic,
            bitis=satir.bitis,
        )

    async def arac_getir(self, arac_id: int) -> Arac | None:
        async with self._oturum_fabrikasi() as oturum:
            satir = await oturum.get(AracTablosu, arac_id)
        if satir is None:
            return None
        return Arac(id=satir.id, plaka=satir.plaka, tip=satir.tip, kapasite=satir.kapasite)
