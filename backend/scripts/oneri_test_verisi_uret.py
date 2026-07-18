"""Test/demo amaçlı: geçmişe dönük, haftalık periyodik sentetik ölçüm verisi üretir.

seed.py'nin önce çalıştırılmış olmasını varsayar (hat/araç/atama kayıtları gerekir).
Simulator'ın gerçek-zamanlı MQTT akışına dokunmaz — doğrudan PostgreSQL'e toplu yazar.

hat_no="34" hattına atanmış araçlar için Pazartesi 08:00-10:00 arası yüksek doluluk
(%80-95), diğer gün/saatlerde normal doluluk (%30-50) enjekte eder — OneriUret'in
SQL sorgusunu ve LLM yorumlamasını gerçekçi biçimde test etmeye yeter.

Çalıştırma (backend/ dizininden):
    python scripts/oneri_test_verisi_uret.py --gun 14
"""

import argparse
import asyncio
import logging
import random
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.adapters.cikan.postgres.baglanti import motor_olustur
from app.adapters.cikan.postgres.tablolar import (
    AracTablosu,
    CihazAtamasiTablosu,
    HatAtamasiTablosu,
    HatTablosu,
    OlcumTablosu,
)
from app.ayarlar import Ayarlar
from app.domain.seviye import doluluk_orani_hesapla, seviye_belirle

logger = logging.getLogger(__name__)

_YOGUN_HAT_NO = "34"
_YOGUN_GUN = 0  # Pazartesi (datetime.weekday())
_YOGUN_SAAT_BASLANGIC = 8
_YOGUN_SAAT_BITIS = 10
_OLCUM_ARALIGI_DK = 15


async def _uret(gun: int, seyrek_ust: float, orta_ust: float) -> None:
    ayarlar = Ayarlar()
    motor = motor_olustur(ayarlar.database_url)
    oturum_fabrikasi = async_sessionmaker(motor, expire_on_commit=False)

    async with oturum_fabrikasi() as oturum:
        yogun_hat = await oturum.scalar(
            select(HatTablosu).where(HatTablosu.hat_no == _YOGUN_HAT_NO)
        )
        if yogun_hat is None:
            raise RuntimeError(
                f"hat_no={_YOGUN_HAT_NO} bulunamadı — önce 'python -m app.seed' çalıştırın"
            )

        atamalar = (
            await oturum.scalars(
                select(HatAtamasiTablosu).where(
                    HatAtamasiTablosu.hat_id == yogun_hat.id,
                    HatAtamasiTablosu.bitis.is_(None),
                )
            )
        ).all()
        if not atamalar:
            raise RuntimeError(f"hat_id={yogun_hat.id} için güncel atama yok")

        arac_id_listesi = [a.arac_id for a in atamalar]
        araclar = {
            arac_id: await oturum.get(AracTablosu, arac_id) for arac_id in arac_id_listesi
        }

        cihaz_atamalari = (
            await oturum.scalars(
                select(CihazAtamasiTablosu).where(
                    CihazAtamasiTablosu.arac_id.in_(arac_id_listesi),
                    CihazAtamasiTablosu.bitis.is_(None),
                )
            )
        ).all()
        cihaz_id_by_arac = {a.arac_id: a.cihaz_id for a in cihaz_atamalari}

        bitis = datetime.now(UTC)
        baslangic = bitis - timedelta(days=gun)
        sayaclar = dict.fromkeys(cihaz_id_by_arac.values(), 1)

        satirlar: list[OlcumTablosu] = []
        an = baslangic
        while an <= bitis:
            for arac_id, cihaz_id in cihaz_id_by_arac.items():
                arac = araclar[arac_id]
                yogun_saatte = _YOGUN_SAAT_BASLANGIC <= an.hour < _YOGUN_SAAT_BITIS
                if an.weekday() == _YOGUN_GUN and yogun_saatte:
                    doluluk_hedef = random.uniform(0.80, 0.95)
                else:
                    doluluk_hedef = random.uniform(0.30, 0.50)
                kisi_sayisi = round(doluluk_hedef * arac.kapasite)
                oran = doluluk_orani_hesapla(kisi_sayisi, arac.kapasite)
                seviye = seviye_belirle(oran, seyrek_ust, orta_ust)

                satirlar.append(
                    OlcumTablosu(
                        cihaz_id=cihaz_id,
                        arac_id=arac_id,
                        hat_id=yogun_hat.id,
                        sira_no=sayaclar[cihaz_id],
                        kisi_sayisi=kisi_sayisi,
                        doluluk_orani=oran,
                        seviye=seviye,
                        olcum_zamani=an,
                    )
                )
                sayaclar[cihaz_id] += 1
            an += timedelta(minutes=_OLCUM_ARALIGI_DK)

        oturum.add_all(satirlar)
        await oturum.commit()
        logger.info("üretilen ölçüm sayısı: %d", len(satirlar))

    await motor.dispose()


def _ayristir() -> argparse.Namespace:
    ayristirici = argparse.ArgumentParser(
        description="Öneri motoru test/demo amaçlı geçmişe dönük veri üretici"
    )
    ayristirici.add_argument("--gun", type=int, default=14, help="Kaç günlük geçmiş üretilsin")
    return ayristirici.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    argumanlar = _ayristir()
    ayarlar = Ayarlar()
    asyncio.run(
        _uret(argumanlar.gun, ayarlar.seviye_seyrek_ust, ayarlar.seviye_orta_ust)
    )
