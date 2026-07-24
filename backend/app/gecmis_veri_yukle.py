"""30 günlük geçmiş yoğunluk verisi (backfill): AI öneri motorunun haftalık
örüntü tespiti, Dashboard trend grafiği ve Son Uyarılar akışı (son birkaç
saat) için gerçekçi, istatistiksel olarak yakalanabilir ölçüm geçmişi üretir.

`python -m app.gecmis_veri_yukle` — seed'den SONRA, her `docker compose up`
çalıştığında tekrar çalıştırılması BEKLENİR (kayan pencere): her hat için
30 gün öncesinden ŞU ANA kadar kesintisiz veri garanti edilir. Uyarı
motoru yalnız son birkaç saate baktığı için (bkz. app/application/
uyari_uret.py) container'ın kapalı kaldığı süre boyunca oluşan boşluk her
seferinde otomatik doldurulur.

`OlcumIsleyici`/atama-çözümleme akışını KULLANMAZ: hat_id/arac_id/doluluk_orani/
seviye zaten OlcumTablosu'nda denormalize kolonlar, doğrudan yazılır (mevcut
HatAtamasiTablosu.baslangic seed'de "şimdi - 2 gün"den başladığı için 30 gün
geriye giden backfill zaten atama penceresine giremez).

Kayan pencere: her çalıştırmada 30 günden eski ölçümler silinir, sonra her
hat için (varsa) en son ölçüm zamanından, yoksa 30 gün öncesinden başlayarak
şimdiye kadar eksik olan günler üretilir. `sira_no` UNIQUE kısıtı zaten
tekrar yazımı ON CONFLICT DO NOTHING ile güvenli kılar.
"""

import asyncio
import logging
import random
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete as sa_delete
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


async def _eski_veriyi_temizle(oturum: AsyncSession, esik: datetime) -> int:
    """Kayan pencere: esik'ten eski ölçümleri siler (30 günden fazla biriktirmesin)."""
    sonuc = await oturum.execute(sa_delete(OlcumTablosu).where(OlcumTablosu.olcum_zamani < esik))
    await oturum.commit()
    return sonuc.rowcount


async def _hat_son_olcum_zamanlarini_al(
    oturum: AsyncSession, hat_idleri: list[int]
) -> dict[int, datetime]:
    """hat_id -> o hattaki en güncel ölçüm zamanı (yoksa sözlükte anahtar olmaz)."""
    ifade = (
        select(OlcumTablosu.hat_id, func.max(OlcumTablosu.olcum_zamani))
        .where(OlcumTablosu.hat_id.in_(hat_idleri))
        .group_by(OlcumTablosu.hat_id)
    )
    satirlar = (await oturum.execute(ifade)).all()
    return dict(satirlar)


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


def _hat_olcumlerini_uret(
    esleme: dict, sira_no_baslangici: int, son_olcum: datetime | None, bitis: datetime
) -> list[dict]:
    """son_olcum varsa ondan SONRAki güne, yoksa 30 gün öncesine kadar geriye
    gidip bitis'e (şimdi) kadar eksik olan günleri üretir — kayan pencere
    tamamlaması, tam yeniden üretim değil.
    """
    hat_no = esleme["hat_no"]
    desen = HAT_DESENLERI.get(hat_no)
    if desen is None:
        logger.warning("hat_no=%s için yoğunluk deseni tanımlı değil, atlanıyor", hat_no)
        return []

    ayarlar = Ayarlar()
    tam_gecmis_baslangici = (bitis - timedelta(days=GUN_PENCERESI)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    if son_olcum is not None:
        # Bir sonraki günün başından devam et — aynı günü iki kez üretme.
        ertesi_gun = (son_olcum + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        baslangic_gunu = max(tam_gecmis_baslangici, ertesi_gun)
    else:
        baslangic_gunu = tam_gecmis_baslangici

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
            sira_no -= 1
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


async def _cihaz_en_kucuk_sira_nolarini_al(
    oturum: AsyncSession, cihaz_idleri: list[str]
) -> dict[str, int]:
    """cihaz_id -> o cihazdaki en küçük (en negatif) sira_no; backfill sıra
    numaraları hep negatiftir, bir sonraki parti bu değerin altından devam eder.
    """
    ifade = (
        select(OlcumTablosu.cihaz_id, func.min(OlcumTablosu.sira_no))
        .where(OlcumTablosu.cihaz_id.in_(cihaz_idleri), OlcumTablosu.sira_no < 0)
        .group_by(OlcumTablosu.cihaz_id)
    )
    satirlar = (await oturum.execute(ifade)).all()
    return dict(satirlar)


async def _calistir() -> None:
    ayarlar = Ayarlar()
    motor = motor_olustur(ayarlar.database_url)
    oturum_fabrikasi = async_sessionmaker(motor, expire_on_commit=False)

    bitis = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    esik = bitis - timedelta(days=GUN_PENCERESI)

    async with oturum_fabrikasi() as oturum:
        eslemeler = await _hat_arac_cihaz_eslesmelerini_al(oturum)

    if not eslemeler:
        logger.warning("hat-araç-cihaz eşlemesi bulunamadı (seed çalıştırılmış mı?), çıkılıyor")
        await motor.dispose()
        return

    async with oturum_fabrikasi() as oturum:
        silinen = await _eski_veriyi_temizle(oturum, esik)
    if silinen:
        logger.info("%d günden eski %d ölçüm silindi (kayan pencere)", GUN_PENCERESI, silinen)

    hat_idleri = [e["hat_id"] for e in eslemeler]
    cihaz_idleri = [e["cihaz_id"] for e in eslemeler]
    async with oturum_fabrikasi() as oturum:
        son_olcumler = await _hat_son_olcum_zamanlarini_al(oturum, hat_idleri)
        en_kucuk_sira_nolar = await _cihaz_en_kucuk_sira_nolarini_al(oturum, cihaz_idleri)

    tum_satirlar: list[dict] = []
    for esleme in eslemeler:
        sira_no_baslangici = en_kucuk_sira_nolar.get(esleme["cihaz_id"], _SIRA_NO_BASLANGICI) - 1
        son_olcum = son_olcumler.get(esleme["hat_id"])
        satirlar = _hat_olcumlerini_uret(esleme, sira_no_baslangici, son_olcum, bitis)
        tum_satirlar.extend(satirlar)

    if not tum_satirlar:
        logger.info("tüm hatlar zaten güncel, eklenecek yeni ölçüm yok")
        await motor.dispose()
        return

    logger.info("toplam %d yeni ölçüm satırı üretildi, yazılıyor...", len(tum_satirlar))
    yazilan = await _toplu_yaz(oturum_fabrikasi, tum_satirlar)
    logger.info("geçmiş veri güncellendi: %d satır yazıldı (%d üretilmişti)", yazilan, len(tum_satirlar))

    await motor.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(_calistir())
