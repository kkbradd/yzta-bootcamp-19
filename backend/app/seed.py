"""Tohum verisi: Üsküdar/Beykoz temalı 11 hat (gerçek İETT 15 serisi durak
isimlerinden derlenmiş, hat başına 8-13 durak), 31 durak, 12 araç, cihazlar
ve güncel atamalar (plan Bölüm 6'nın genişletilmiş hali — hat-durak ilişkisi dahil).

`python -m app.seed` ile çalıştırılır. Tekrar çalıştırılabilir: tohum zaten
yüklüyse hiçbir satır yazılmaz (bitti tanımı: satır sayıları değişmez).
Not: mevcut bir veritabanında daha önce eski (3 hatlı) tohum yüklenmişse bu
kontrol "tohum zaten var" der ve yeni Üsküdar verisini eklemez — güncel
veriyi görmek için veritabanı sıfırlanmalı (`docker compose down -v`).
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.cikan.guvenlik import sifre_hashle
from app.adapters.cikan.postgres.baglanti import motor_olustur, tablolari_olustur
from app.adapters.cikan.postgres.tablolar import (
    AracTablosu,
    CihazAtamasiTablosu,
    CihazTablosu,
    DurakTablosu,
    HatAtamasiTablosu,
    HatDuraklariTablosu,
    HatTablosu,
    KullaniciTablosu,
)
from app.ayarlar import Ayarlar
from app.domain.modeller import CIHAZ_TIPI_ARAC, CIHAZ_TIPI_DURAK

logger = logging.getLogger(__name__)

# (durak adı, enlem, boylam) — gerçek İETT 15/15B hat güzergahlarındaki durak
# isimlerinden derlenmiştir; aynı durak birden fazla hatta kullanılarak
# aktarma noktaları (ortak duraklar) doğal olarak oluşur.
DURAKLAR = [
    ("Üsküdar İskele", 41.0214, 29.0139),
    ("Doğancılar", 41.0247, 29.0117),
    ("Bağlarbaşı", 41.0219, 29.0295),
    ("Selimiye", 41.0198, 29.0069),
    ("Altunizade", 41.0128, 29.0432),
    ("Çengelköy", 41.0453, 29.0552),
    ("Kuzguncuk", 41.0339, 29.0311),
    ("Beylerbeyi", 41.0421, 29.0430),
    ("Kısıklı", 41.0092, 29.0631),
    ("Validebağ", 41.0117, 29.0374),
    ("Küçük Çamlıca", 41.0034, 29.0742),
    ("Ümraniye Merkez", 41.0165, 29.1128),
    ("Acıbadem", 41.0016, 29.0350),
    ("Bulgurlu", 41.0087, 29.0654),
    ("Kandilli", 41.0602, 29.0578),
    ("Paşalimanı", 41.0271, 29.0221),
    ("Tekel Deposu", 41.0243, 29.0169),
    ("Beylerbeyi Sarayı", 41.0411, 29.0420),
    ("Yalıboyu", 41.0398, 29.0400),
    ("Vaniköy", 41.0567, 29.0592),
    ("Kuleli", 41.0533, 29.0587),
    ("Anadolu Hisarı", 41.0857, 29.0731),
    ("Kanlıca", 41.0918, 29.0640),
    ("Beykoz", 41.1279, 29.0965),
    ("Paşabahçe", 41.1103, 29.0812),
    ("Çubuklu", 41.1005, 29.0699),
    ("Ümraniye Belediyesi", 41.0257, 29.1072),
    ("Ümraniye Eğitim Araştırma Hastanesi", 41.0173, 29.0942),
    ("Elmalıkent", 41.0154, 29.1035),
    ("Tantavi", 41.0226, 29.0864),
    ("Gökçe Sokak", 41.0309, 29.0642),
]

# (hat_no, ad, [durak adları — DURAKLAR'a referans, sırayla geçiş sırası])
HATLAR = [
    ("15U", "Üsküdar – Ümraniye", [
        "Üsküdar İskele", "Doğancılar", "Bağlarbaşı", "Altunizade", "Acıbadem",
        "Bulgurlu", "Gökçe Sokak", "Tantavi", "Elmalıkent", "Ümraniye Eğitim Araştırma Hastanesi", "Ümraniye Merkez",
    ]),
    ("15A", "Üsküdar – Kısıklı", [
        "Üsküdar İskele", "Doğancılar", "Bağlarbaşı", "Selimiye", "Validebağ",
        "Bulgurlu", "Gökçe Sokak", "Kısıklı",
    ]),
    ("15B", "Üsküdar – Çengelköy", [
        "Üsküdar İskele", "Selimiye", "Paşalimanı", "Kuzguncuk", "Beylerbeyi Sarayı",
        "Beylerbeyi", "Yalıboyu", "Vaniköy", "Kuleli", "Çengelköy",
    ]),
    ("15C", "Üsküdar – Kandilli", [
        "Üsküdar İskele", "Selimiye", "Kuzguncuk", "Beylerbeyi", "Yalıboyu",
        "Vaniköy", "Kuleli", "Kandilli",
    ]),
    ("15E", "Bağlarbaşı – Ümraniye", [
        "Bağlarbaşı", "Altunizade", "Acıbadem", "Bulgurlu", "Gökçe Sokak",
        "Tantavi", "Elmalıkent", "Ümraniye Belediyesi", "Ümraniye Merkez",
    ]),
    ("15F", "Altunizade – Küçük Çamlıca", [
        "Altunizade", "Acıbadem", "Validebağ", "Bulgurlu", "Gökçe Sokak",
        "Kısıklı", "Tantavi", "Küçük Çamlıca",
    ]),
    ("15G", "Üsküdar – Altunizade", [
        "Üsküdar İskele", "Doğancılar", "Bağlarbaşı", "Selimiye", "Paşalimanı",
        "Validebağ", "Acıbadem", "Altunizade",
    ]),
    ("15Y", "Kısıklı – Küçük Çamlıca", [
        "Kısıklı", "Validebağ", "Bulgurlu", "Gökçe Sokak", "Acıbadem",
        "Tantavi", "Elmalıkent", "Küçük Çamlıca",
    ]),
    ("15R", "Çengelköy – Kısıklı", [
        "Çengelköy", "Kuleli", "Beylerbeyi", "Yalıboyu", "Beylerbeyi Sarayı",
        "Bulgurlu", "Gökçe Sokak", "Kısıklı",
    ]),
    ("15S", "Üsküdar – Kuzguncuk (Sahil)", [
        "Üsküdar İskele", "Tekel Deposu", "Paşalimanı", "Selimiye", "Doğancılar",
        "Bağlarbaşı", "Validebağ", "Kuzguncuk",
    ]),
    ("15", "Beykoz – Üsküdar", [
        "Beykoz", "Paşabahçe", "Çubuklu", "Kanlıca", "Anadolu Hisarı",
        "Kandilli", "Kuleli", "Vaniköy", "Çengelköy", "Beylerbeyi", "Yalıboyu",
        "Kuzguncuk", "Üsküdar İskele",
    ]),
]

# (plaka, tip, kapasite, atanacağı hat_no) — her hatta en az 1 araç.
# Tüm araçlar aynı tip/kapasite (otobüs, 60): doluluk oranı hesapları ve
# backfill/geçmiş veri üretimi (bkz. app/gecmis_veri_yukle.py) tek bir
# kapasite üzerinden tutarlı kalsın diye kasıtlı olarak tekilleştirildi.
ARACLAR = [
    ("34 HAT 001", "otobus", 60, "15"),
    ("34 HAT 002", "otobus", 60, "15"),
    ("34 HAT 003", "otobus", 60, "15A"),
    ("34 HAT 004", "otobus", 60, "15B"),
    ("34 HAT 005", "otobus", 60, "15C"),
    ("34 HAT 006", "otobus", 60, "15E"),
    ("34 HAT 007", "otobus", 60, "15F"),
    ("34 HAT 008", "otobus", 60, "15G"),
    ("34 HAT 009", "otobus", 60, "15Y"),
    ("34 HAT 010", "otobus", 60, "15R"),
    ("34 HAT 011", "otobus", 60, "15S"),
    ("34 HAT 012", "otobus", 60, "15U"),
]
YAZILIM_SURUMU = "1.0.0"

DEMO_KULLANICI_EPOSTA = "admin@demo.com"
DEMO_KULLANICI_SIFRE = "admin123"


async def tohumla(oturum: AsyncSession) -> bool:
    """Tohum verisini yükler; veri zaten varsa dokunmadan False döner."""
    hat_sayisi = await oturum.scalar(select(func.count()).select_from(HatTablosu))
    if hat_sayisi:
        return False

    # Atamalar geçmişten başlar: filo tohumdan önce de atanmıştı ve gecikmeli
    # (tünel) ölçümlerin çekim damgaları atama penceresine düşebilmeli.
    atama_baslangici = datetime.now(UTC) - timedelta(days=2)

    # Evre 1 — varlıklar: FK hedefleri tek flush ile veritabanına iner.
    hatlar = {hat_no: HatTablosu(hat_no=hat_no, ad=ad) for hat_no, ad, _ in HATLAR}
    duraklar = {
        ad: DurakTablosu(ad=ad, enlem=enlem, boylam=boylam) for ad, enlem, boylam in DURAKLAR
    }
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
    oturum.add_all(
        [*hatlar.values(), *duraklar.values(), *araclar, *arac_cihazlari, durak_cihazi]
    )
    await oturum.flush()

    # Evre 1.5 — hat-durak ilişkileri (sıralı; ortak duraklar aktarma noktalarını oluşturur).
    for hat_no, _, durak_adlari in HATLAR:
        for sira, durak_adi in enumerate(durak_adlari):
            oturum.add(
                HatDuraklariTablosu(
                    hat_id=hatlar[hat_no].id, durak_id=duraklar[durak_adi].id, sira=sira
                )
            )
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
        CihazAtamasiTablosu(
            cihaz_id=durak_cihazi.id,
            durak_id=duraklar["Üsküdar İskele"].id,
            baslangic=atama_baslangici,
        )
    )

    await oturum.commit()
    return True


async def kullanici_tohumla(oturum: AsyncSession) -> bool:
    """Demo kullanıcıyı yükler; zaten varsa dokunmadan False döner."""
    mevcut = await oturum.scalar(
        select(func.count())
        .select_from(KullaniciTablosu)
        .where(KullaniciTablosu.eposta == DEMO_KULLANICI_EPOSTA)
    )
    if mevcut:
        return False
    oturum.add(
        KullaniciTablosu(
            eposta=DEMO_KULLANICI_EPOSTA,
            sifre_hash=sifre_hashle(DEMO_KULLANICI_SIFRE),
        )
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
    async with oturum_fabrikasi() as oturum:
        kullanici_yuklendi = await kullanici_tohumla(oturum)
    logger.info(
        "kullanıcı tohumu %s", "yüklendi" if kullanici_yuklendi else "zaten yüklü, değişiklik yok"
    )
    await motor.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(_calistir())
