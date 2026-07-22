"""30 günlük geçmiş yoğunluk verisi (backfill): AI öneri motorunun haftalık
örüntü tespiti ve Dashboard trend grafiği için gerçekçi, istatistiksel olarak
yakalanabilir ölçüm geçmişi üretir.

`python -m app.gecmis_veri_yukle` — seed'den SONRA, elle/CI dışı çalıştırılır.
`OlcumIsleyici`/atama-çözümleme akışını KULLANMAZ: hat_id/arac_id/doluluk_orani/
seviye zaten OlcumTablosu'nda denormalize kolonlar, doğrudan yazılır (mevcut
HatAtamasiTablosu.baslangic seed'de "şimdi - 2 gün"den başladığı için 30 gün
geriye giden backfill zaten atama penceresine giremez).

Idempotent: 25 günden eski herhangi bir ölçüm varsa script hiçbir şey
yazmadan çıkar (atomik — ya tam çalışır ya hiç, kısmi tamamlama yok).
"""

import asyncio
import logging
import random
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.cikan.postgres.baglanti import motor_olustur
from app.adapters.cikan.postgres.tablolar import (
    AracTablosu,
    CihazAtamasiTablosu,
    CihazTablosu,
    HatAtamasiTablosu,
    HatTablosu,
    OlcumTablosu,
)
from app.ayarlar import Ayarlar
from app.domain.seviye import doluluk_orani_hesapla, seviye_belirle

logger = logging.getLogger(__name__)

GUN_PENCERESI = 30
SEFER_SIKLIKLARI_DK = (10, 15, 20, 30)
_BATCH_BOYUTU = 2000
_SIRA_NO_BASLANGICI = -1_000_000  # MQTT simülatörünün int(time.time()) ile hiç çakışmaz.

# hat_no -> yoğunluk deseni. "saat" paternleri her gün aynı saat diliminde
# yoğun; "gun" paterni yalnız belirtilen haftanın günü/günlerinde yoğun.
# gun_no kodlaması PostgreSQL EXTRACT(DOW) ile birebir: 0=Pazar..6=Cumartesi.
HAT_DESENLERI = {
    "15": {"tip": "saat", "baslangic": 6, "bitis": 9},
    "15U": {"tip": "saat", "baslangic": 6, "bitis": 9},
    "15A": {"tip": "saat", "baslangic": 6, "bitis": 9},
    "15E": {"tip": "saat", "baslangic": 6, "bitis": 9},
    "15B": {"tip": "saat", "baslangic": 18, "bitis": 20},
    "15C": {"tip": "saat", "baslangic": 18, "bitis": 20},
    "15G": {"tip": "saat", "baslangic": 18, "bitis": 20},
    "15F": {"tip": "saat", "baslangic": 18, "bitis": 20},
    "15Y": {"tip": "gun", "gunler": (1,)},  # Pazartesi
    "15R": {"tip": "gun", "gunler": (5,)},  # Cuma
    "15S": {"tip": "gun", "gunler": (0, 6)},  # Hafta sonu
}

_HAFTA_SONU = (0, 6)


def _dow(zaman: datetime) -> int:
    """PostgreSQL EXTRACT(DOW) ile birebir: 0=Pazar..6=Cumartesi. weekday() KULLANMA."""
    return zaman.isoweekday() % 7


def _kisi_sayisi_uret(zaman: datetime, desen: dict) -> int:
    """Saat + gün + hattın yoğunluk desenine göre gerçekçi kişi sayısı üretir."""
    saat = zaman.hour
    gun_no = _dow(zaman)

    yogun_mu = False
    if desen["tip"] == "saat":
        yogun_mu = desen["baslangic"] <= saat < desen["bitis"]
        # Saat-bazlı hatlarda hafta sonu yoğunluğu bir kademe düşürülür —
        # aksi halde her gün aynı davrandığından günler-arası karşılaştırma
        # (_karsilastirma_ekle) sıfıra yakın fark bulur ve öneri motoru
        # BELIRGIN_SAPMA_ESIGI eşiğini hiç geçemez.
        if yogun_mu and gun_no in _HAFTA_SONU:
            temel_alt, temel_ust = 20, 45
        elif yogun_mu:
            temel_alt, temel_ust = 55, 75
        elif 7 <= saat < 22:
            temel_alt, temel_ust = 20, 45
        else:
            temel_alt, temel_ust = 5, 20
    else:  # "gun"
        yogun_mu = gun_no in desen["gunler"] and 7 <= saat < 21
        if yogun_mu:
            temel_alt, temel_ust = 55, 75
        elif 7 <= saat < 22:
            temel_alt, temel_ust = 20, 45
        else:
            temel_alt, temel_ust = 5, 20

    temel = random.randint(temel_alt, temel_ust)
    gurultulu = round(temel * random.uniform(0.9, 1.1))
    return max(0, min(90, gurultulu))  # 90: kasıtlı aşırı-doluluk üst sınırı (kapasite 60'ın üstü de olabilir)


def _gun_sefer_zamanlarini_uret(gun_baslangici: datetime) -> list[datetime]:
    """O güne özel rastgele sefer sıklığıyla (10/15/20/30dk) sefer zamanları üretir."""
    sefer_dk = random.choice(SEFER_SIKLIKLARI_DK)
    sefer_sayisi = 1440 // sefer_dk
    return [gun_baslangici + timedelta(minutes=sefer_dk * i) for i in range(sefer_sayisi)]


async def _zaten_yuklu_mu(oturum: AsyncSession) -> bool:
    esik = datetime.now(UTC) - timedelta(days=25)
    sayi = await oturum.scalar(
        select(func.count()).select_from(OlcumTablosu).where(OlcumTablosu.olcum_zamani < esik)
    )
    return bool(sayi)


async def _hat_arac_cihaz_eslesmelerini_al(oturum: AsyncSession) -> list[dict]:
    """(hat_no, hat_id, arac_id, cihaz_id, kapasite) — güncel atamalardan DB'den okunur."""
    ifade = (
        select(
            HatTablosu.hat_no,
            HatTablosu.id,
            AracTablosu.id,
            CihazTablosu.id,
            AracTablosu.kapasite,
        )
        .join(HatAtamasiTablosu, HatAtamasiTablosu.hat_id == HatTablosu.id)
        .join(AracTablosu, AracTablosu.id == HatAtamasiTablosu.arac_id)
        .join(CihazAtamasiTablosu, CihazAtamasiTablosu.arac_id == AracTablosu.id)
        .join(CihazTablosu, CihazTablosu.id == CihazAtamasiTablosu.cihaz_id)
        .where(
            HatAtamasiTablosu.bitis.is_(None),
            CihazAtamasiTablosu.bitis.is_(None),
        )
    )
    satirlar = (await oturum.execute(ifade)).all()
    return [
        {"hat_no": hat_no, "hat_id": hat_id, "arac_id": arac_id, "cihaz_id": cihaz_id, "kapasite": kapasite}
        for hat_no, hat_id, arac_id, cihaz_id, kapasite in satirlar
    ]


def _hat_olcumlerini_uret(esleme: dict, sira_no_baslangici: int) -> list[dict]:
    hat_no = esleme["hat_no"]
    desen = HAT_DESENLERI.get(hat_no)
    if desen is None:
        logger.warning("hat_no=%s için yoğunluk deseni tanımlı değil, atlanıyor", hat_no)
        return []

    ayarlar = Ayarlar()
    bitis = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    baslangic_gunu = (bitis - timedelta(days=GUN_PENCERESI)).replace(hour=0)

    satirlar: list[dict] = []
    sira_no = sira_no_baslangici
    gun = baslangic_gunu
    while gun < bitis:
        for zaman in _gun_sefer_zamanlarini_uret(gun):
            if zaman >= bitis:
                continue
            kisi_sayisi = _kisi_sayisi_uret(zaman, desen)
            oran = doluluk_orani_hesapla(kisi_sayisi, esleme["kapasite"])
            seviye = seviye_belirle(oran, ayarlar.seviye_seyrek_ust, ayarlar.seviye_orta_ust)
            satirlar.append(
                {
                    "cihaz_id": esleme["cihaz_id"],
                    "arac_id": esleme["arac_id"],
                    "hat_id": esleme["hat_id"],
                    "sira_no": sira_no,
                    "kisi_sayisi": kisi_sayisi,
                    "doluluk_orani": oran,
                    "seviye": seviye,
                    "olcum_zamani": zaman,
                }
            )
            sira_no += 1
        gun += timedelta(days=1)

    logger.info("hat_no=%s için %d ölçüm üretildi", hat_no, len(satirlar))
    return satirlar


async def _toplu_yaz(oturum_fabrikasi: async_sessionmaker[AsyncSession], satirlar: list[dict]) -> int:
    toplam = 0
    for i in range(0, len(satirlar), _BATCH_BOYUTU):
        parca = satirlar[i : i + _BATCH_BOYUTU]
        ifade = pg_insert(OlcumTablosu).values(parca).on_conflict_do_nothing(
            constraint="uq_olcumler_cihaz_sira"
        )
        async with oturum_fabrikasi() as oturum:
            sonuc = await oturum.execute(ifade)
            await oturum.commit()
        toplam += sonuc.rowcount
    return toplam


async def _calistir() -> None:
    ayarlar = Ayarlar()
    motor = motor_olustur(ayarlar.database_url)
    oturum_fabrikasi = async_sessionmaker(motor, expire_on_commit=False)

    async with oturum_fabrikasi() as oturum:
        if await _zaten_yuklu_mu(oturum):
            logger.info("geçmiş veri zaten yüklü, çıkılıyor")
            await motor.dispose()
            return
        eslemeler = await _hat_arac_cihaz_eslesmelerini_al(oturum)

    if not eslemeler:
        logger.warning("hat-araç-cihaz eşlemesi bulunamadı (seed çalıştırılmış mı?), çıkılıyor")
        await motor.dispose()
        return

    tum_satirlar: list[dict] = []
    sira_no = _SIRA_NO_BASLANGICI
    for esleme in eslemeler:
        satirlar = _hat_olcumlerini_uret(esleme, sira_no)
        sira_no -= len(satirlar) + 1
        tum_satirlar.extend(satirlar)

    logger.info("toplam %d ölçüm satırı üretildi, yazılıyor...", len(tum_satirlar))
    yazilan = await _toplu_yaz(oturum_fabrikasi, tum_satirlar)
    logger.info("geçmiş veri yüklendi: %d satır yazıldı (%d üretilmişti)", yazilan, len(tum_satirlar))

    await motor.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(_calistir())
