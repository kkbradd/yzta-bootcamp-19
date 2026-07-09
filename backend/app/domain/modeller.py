"""Saf iş nesneleri — dış kütüphane import edilmez (bkz. tests/unit/test_mimari.py).

Alan adları plan Bölüm 6'daki sözleşmeyle birebir aynıdır; panel ekibi
bu adlara göre geliştirme yapar, değiştirilmez.
"""

from dataclasses import dataclass
from datetime import datetime

CIHAZ_TIPI_ARAC = "arac"
CIHAZ_TIPI_DURAK = "durak"
CIHAZ_TIPLERI = (CIHAZ_TIPI_ARAC, CIHAZ_TIPI_DURAK)


@dataclass(frozen=True, slots=True)
class Hat:
    id: int
    hat_no: str
    ad: str


@dataclass(frozen=True, slots=True)
class Arac:
    id: int
    plaka: str
    tip: str
    kapasite: int


@dataclass(frozen=True, slots=True)
class Durak:
    id: int
    ad: str
    enlem: float
    boylam: float


@dataclass(frozen=True, slots=True)
class Cihaz:
    id: str
    tip: str  # CIHAZ_TIPLERI'nden biri
    yazilim_surumu: str | None = None


@dataclass(frozen=True, slots=True)
class HatAtamasi:
    id: int
    hat_id: int
    arac_id: int
    baslangic: datetime
    bitis: datetime | None = None  # None = güncel atama


@dataclass(frozen=True, slots=True)
class CihazAtamasi:
    id: int
    cihaz_id: str
    baslangic: datetime
    arac_id: int | None = None  # arac_id ile durak_id'den tam biri dolu olur
    durak_id: int | None = None
    bitis: datetime | None = None  # None = güncel atama


@dataclass(frozen=True, slots=True)
class Olcum:
    """Tek bir yoğunluk ölçümü; arac/hat alanları ingest anında denormalize edilir."""

    cihaz_id: str
    sira_no: int
    kisi_sayisi: int
    olcum_zamani: datetime
    arac_id: int | None = None  # duraklarda None
    hat_id: int | None = None  # duraklarda None
    doluluk_orani: float | None = None  # duraklarda None (kapasite yok)
    seviye: str | None = None  # 'seyrek' | 'orta' | 'yogun'; duraklarda None
