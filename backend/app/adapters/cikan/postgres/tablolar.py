"""PostgreSQL tablo tanımları — plan Bölüm 6'daki şemanın birebir karşılığı.

Tüm zaman alanları TIMESTAMPTZ (UTC). Kritik kurallar:
- olcumler üzerinde UNIQUE(cihaz_id, sira_no): MQTT QoS 1 mükerrerlerini eler.
- Atama tabloları zaman aralıklıdır; güncel atama = bitis IS NULL.
- olcumler.arac_id/hat_id ingest anında denormalize edilir (çekim damgasına göre).
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import DateTime

from app.domain.modeller import CIHAZ_TIPLERI

_CIHAZ_TIPLERI_SQL = ", ".join(f"'{tip}'" for tip in CIHAZ_TIPLERI)


class Taban(DeclarativeBase):
    type_annotation_map = {
        datetime: DateTime(timezone=True),
        str: Text,
    }


class HatTablosu(Taban):
    __tablename__ = "hatlar"

    id: Mapped[int] = mapped_column(primary_key=True)
    hat_no: Mapped[str] = mapped_column(unique=True)
    ad: Mapped[str]


class AracTablosu(Taban):
    __tablename__ = "araclar"
    __table_args__ = (CheckConstraint("kapasite > 0", name="ck_araclar_kapasite_pozitif"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    plaka: Mapped[str] = mapped_column(unique=True)
    tip: Mapped[str]
    kapasite: Mapped[int]


class DurakTablosu(Taban):
    __tablename__ = "duraklar"

    id: Mapped[int] = mapped_column(primary_key=True)
    ad: Mapped[str]
    enlem: Mapped[float]
    boylam: Mapped[float]


class CihazTablosu(Taban):
    __tablename__ = "cihazlar"
    __table_args__ = (
        CheckConstraint(f"tip IN ({_CIHAZ_TIPLERI_SQL})", name="ck_cihazlar_tip"),
    )

    id: Mapped[str] = mapped_column(primary_key=True)  # ör. "edge_0042"
    tip: Mapped[str]
    yazilim_surumu: Mapped[str | None]


class HatAtamasiTablosu(Taban):
    __tablename__ = "hat_atamalari"

    id: Mapped[int] = mapped_column(primary_key=True)
    hat_id: Mapped[int] = mapped_column(ForeignKey("hatlar.id"))
    arac_id: Mapped[int] = mapped_column(ForeignKey("araclar.id"))
    baslangic: Mapped[datetime]
    bitis: Mapped[datetime | None]  # NULL = güncel atama


class CihazAtamasiTablosu(Taban):
    __tablename__ = "cihaz_atamalari"
    __table_args__ = (
        # Cihaz ya bir araca ya bir durağa bağlıdır — ikisinden tam biri.
        CheckConstraint("(arac_id IS NULL) <> (durak_id IS NULL)", name="ck_cihaz_atama_hedef"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cihaz_id: Mapped[str] = mapped_column(ForeignKey("cihazlar.id"))
    arac_id: Mapped[int | None] = mapped_column(ForeignKey("araclar.id"))
    durak_id: Mapped[int | None] = mapped_column(ForeignKey("duraklar.id"))
    baslangic: Mapped[datetime]
    bitis: Mapped[datetime | None]  # NULL = güncel atama


class OlcumTablosu(Taban):
    __tablename__ = "olcumler"
    __table_args__ = (
        UniqueConstraint("cihaz_id", "sira_no", name="uq_olcumler_cihaz_sira"),
        CheckConstraint("kisi_sayisi >= 0", name="ck_olcumler_kisi_sayisi_negatif_degil"),
        Index("ix_olcumler_cihaz_zaman", "cihaz_id", text("olcum_zamani DESC")),
        Index("ix_olcumler_hat_zaman", "hat_id", text("olcum_zamani DESC")),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cihaz_id: Mapped[str] = mapped_column(ForeignKey("cihazlar.id"))
    arac_id: Mapped[int | None] = mapped_column(ForeignKey("araclar.id"))
    hat_id: Mapped[int | None] = mapped_column(ForeignKey("hatlar.id"))
    sira_no: Mapped[int] = mapped_column(BigInteger)
    kisi_sayisi: Mapped[int]
    doluluk_orani: Mapped[float | None]  # duraklarda NULL
    seviye: Mapped[str | None]  # 'seyrek' | 'orta' | 'yogun'; duraklarda NULL
    olcum_zamani: Mapped[datetime]
