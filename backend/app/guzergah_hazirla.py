"""OSRM ile hat güzergahı polyline'ı üretir ve guzergahlar tablosuna yazar.

`python -m app.guzergah_hazirla` — seed'den SONRA, elle/CI dışı çalıştırılır.
Idempotent: guzergahlar tablosunda hat_id zaten varsa o hat atlanır (OSRM'e
tekrar gidilmez). Ağ hatasında (timeout/5xx) o hat için log+skip, süreç
devam eder — kısmi başarı kabul edilir (bir dahaki çalıştırmada eksikler
tamamlanır). Seed'den ayrı tutulma nedeni: OSRM public demo API dış ağ
bağımlılığı, seed.py'nin hızlı/deterministik/CI-güvenli kalması gerekiyor.
"""

import asyncio
import logging
from datetime import UTC, datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.cikan.postgres.baglanti import motor_olustur
from app.adapters.cikan.postgres.tablolar import (
    DurakTablosu,
    GuzergahTablosu,
    HatDuraklariTablosu,
    HatTablosu,
)
from app.ayarlar import Ayarlar

logger = logging.getLogger(__name__)

OSRM_TABAN = "http://router.project-osrm.org"
_ISTEK_ARASI_BEKLEME_SN = 1.0  # public demo API nezaket gecikmesi (rate-limit)


async def _hat_koordinatlarini_al(oturum: AsyncSession, hat_id: int) -> list[tuple[float, float]]:
    ifade = (
        select(DurakTablosu.enlem, DurakTablosu.boylam)
        .join(HatDuraklariTablosu, HatDuraklariTablosu.durak_id == DurakTablosu.id)
        .where(HatDuraklariTablosu.hat_id == hat_id)
        .order_by(HatDuraklariTablosu.sira)
    )
    satirlar = (await oturum.execute(ifade)).all()
    return [(enlem, boylam) for enlem, boylam in satirlar]


async def _osrm_rota_cek(
    istemci: httpx.AsyncClient, noktalar: list[tuple[float, float]]
) -> dict | None:
    # OSRM koordinat sırası lon,lat'tır (domain'in enlem,boylam sırasının tersi).
    koordinat_str = ";".join(f"{boylam},{enlem}" for enlem, boylam in noktalar)
    url = f"{OSRM_TABAN}/route/v1/driving/{koordinat_str}"
    try:
        yanit = await istemci.get(
            url, params={"overview": "full", "geometries": "geojson"}, timeout=15
        )
        yanit.raise_for_status()
        veri = yanit.json()
        if veri.get("code") != "Ok" or not veri.get("routes"):
            logger.warning("OSRM rota bulamadı: %s", veri.get("code"))
            return None
        return veri["routes"][0]
    except (httpx.HTTPError, ValueError) as hata:
        logger.warning("OSRM çağrısı başarısız: %s", hata)
        return None


async def _calistir() -> None:
    ayarlar = Ayarlar()
    motor = motor_olustur(ayarlar.database_url)
    oturum_fabrikasi = async_sessionmaker(motor, expire_on_commit=False)

    async with oturum_fabrikasi() as oturum:
        hat_idleri = (await oturum.scalars(select(HatTablosu.id))).all()
        mevcut = set((await oturum.scalars(select(GuzergahTablosu.hat_id))).all())

    eksikler = [h for h in hat_idleri if h not in mevcut]
    if not eksikler:
        logger.info("tüm hatların güzergahı zaten var, çıkılıyor")
        await motor.dispose()
        return

    async with httpx.AsyncClient() as istemci:
        for hat_id in eksikler:
            async with oturum_fabrikasi() as oturum:
                noktalar = await _hat_koordinatlarini_al(oturum, hat_id)
                if len(noktalar) < 2:
                    logger.warning("hat_id=%s için yetersiz durak, atlanıyor", hat_id)
                    continue
                rota = await _osrm_rota_cek(istemci, noktalar)
                if rota is None:
                    continue
                # GeoJSON [lon,lat] -> domain [lat,lon].
                koordinatlar = [[lat, lon] for lon, lat in rota["geometry"]["coordinates"]]
                oturum.add(
                    GuzergahTablosu(
                        hat_id=hat_id,
                        koordinatlar=koordinatlar,
                        mesafe_metre=rota["distance"],
                        sure_saniye=rota["duration"],
                        olusturulma_zamani=datetime.now(UTC),
                    )
                )
                await oturum.commit()
            logger.info("hat_id=%s güzergahı kaydedildi (%d nokta)", hat_id, len(koordinatlar))
            await asyncio.sleep(_ISTEK_ARASI_BEKLEME_SN)

    await motor.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(_calistir())
