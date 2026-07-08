"""Tohum verisi: 3 hat, 5 araç, 1 durak, 6 cihaz ve güncel atamalar (plan Bölüm 6).

`python -m app.seed` ile çalıştırılır. Tekrar çalıştırılabilir: tohum zaten
yüklüyse hiçbir satır yazılmaz (bitti tanımı: satır sayıları değişmez).
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.cikan.postgres.baglanti import motor_olustur, tablolari_olustur
from app.adapters.cikan.postgres.tablolar import (
    AracTablosu,
    CihazAtamasiTablosu,
    CihazTablosu,
    DurakTablosu,
    HatAtamasiTablosu,
    HatTablosu,
)
from app.ayarlar import Ayarlar
from app.domain.modeller import CIHAZ_TIPI_ARAC, CIHAZ_TIPI_DURAK

logger = logging.getLogger(__name__)

HATLAR = [
    ("34", "Zincirlikuyu – Söğütlüçeşme"),
    ("19T", "Taksim – Tuzla"),
    ("42", "Kadıköy – Ümraniye"),
]
# (plaka, tip, kapasite, atanacağı hat_no)
ARACLAR = [
    ("34 HAT 001", "metrobus", 90, "34"),
    ("34 HAT 002", "metrobus", 90, "34"),
    ("34 HAT 003", "otobus", 60, "19T"),
    ("34 HAT 004", "midibus", 30, "19T"),
    ("34 HAT 005", "midibus", 30, "42"),
]
YAZILIM_SURUMU = "1.0.0"


async def tohumla(oturum: AsyncSession) -> bool:
    """Tohum verisini yükler; veri zaten varsa dokunmadan False döner."""
    hat_sayisi = await oturum.scalar(select(func.count()).select_from(HatTablosu))
    if hat_sayisi:
        return False

    # Atamalar geçmişten başlar: filo tohumdan önce de atanmıştı ve gecikmeli
    # (tünel) ölçümlerin çekim damgaları atama penceresine düşebilmeli.
    atama_baslangici = datetime.now(UTC) - timedelta(days=2)

    # Evre 1 — varlıklar: FK hedefleri tek flush ile veritabanına iner.
    hatlar = {hat_no: HatTablosu(hat_no=hat_no, ad=ad) for hat_no, ad in HATLAR}
    durak = DurakTablosu(ad="Zincirlikuyu", enlem=41.0670, boylam=29.0146)
    araclar = [
        AracTablosu(plaka=plaka, tip=tip, kapasite=kapasite) for plaka, tip, kapasite, _ in ARACLAR
    ]
    arac_cihazlari = [
        CihazTablosu(id=f"edge_{sira:04d}", tip=CIHAZ_TIPI_ARAC, yazilim_surumu=YAZILIM_SURUMU)
        for sira in range(1, len(ARACLAR) + 1)
    ]
    durak_cihazi = CihazTablosu(
        id=f"edge_{len(ARACLAR) + 1:04d}", tip=CIHAZ_TIPI_DURAK, yazilim_surumu=YAZILIM_SURUMU
    )
    oturum.add_all([*hatlar.values(), durak, *araclar, *arac_cihazlari, durak_cihazi])
    await oturum.flush()

    # Evre 2 — güncel atamalar (bitis=None).
    for (_, _, _, hat_no), arac, cihaz in zip(ARACLAR, araclar, arac_cihazlari, strict=True):
        oturum.add_all(
            [
                HatAtamasiTablosu(
                    hat_id=hatlar[hat_no].id, arac_id=arac.id, baslangic=atama_baslangici
                ),
                CihazAtamasiTablosu(cihaz_id=cihaz.id, arac_id=arac.id, baslangic=atama_baslangici),
            ]
        )
    oturum.add(
        CihazAtamasiTablosu(cihaz_id=durak_cihazi.id, durak_id=durak.id, baslangic=atama_baslangici)
    )

    await oturum.commit()
    return True


async def _calistir() -> None:
    ayarlar = Ayarlar()
    motor = motor_olustur(ayarlar.database_url)
    await tablolari_olustur(motor)
    oturum_fabrikasi = async_sessionmaker(motor, expire_on_commit=False)
    async with oturum_fabrikasi() as oturum:
        yuklendi = await tohumla(oturum)
    logger.info("tohum %s", "yüklendi" if yuklendi else "zaten yüklü, değişiklik yok")
    await motor.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(_calistir())
