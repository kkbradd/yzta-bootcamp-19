"""REST okuma uçlarının PostgreSQL sorguları (plan Bölüm 9).

Trend, ölçümleri denormalize hat_id kolonu üzerinden okur (Bölüm 8.1) —
zamansal join yok; gecikmeli ölçümler çekim damgalarıyla doğru kovaya düşer.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.cikan.postgres.tablolar import CihazTablosu, HatTablosu, OlcumTablosu
from app.domain.modeller import Cihaz, Hat, Olcum

_ARALIK_GENISLIKLERI = {"saat": timedelta(hours=1), "15dk": timedelta(minutes=15)}
_KOVA_BASLANGICI = datetime(2000, 1, 1, tzinfo=UTC)  # date_bin çapası (herhangi sabit an)


class PostgresSorgular:
    def __init__(self, oturum_fabrikasi: async_sessionmaker[AsyncSession]) -> None:
        self._oturum_fabrikasi = oturum_fabrikasi

    async def hatlari_listele(self) -> list[Hat]:
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.scalars(select(HatTablosu).order_by(HatTablosu.id))).all()
        return [Hat(id=s.id, hat_no=s.hat_no, ad=s.ad) for s in satirlar]

    async def cihazlari_listele(self) -> list[Cihaz]:
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.scalars(select(CihazTablosu).order_by(CihazTablosu.id))).all()
        return [Cihaz(id=s.id, tip=s.tip, yazilim_surumu=s.yazilim_surumu) for s in satirlar]

    async def hat_trendi(
        self, hat_id: int, baslangic: datetime, bitis: datetime, aralik: str
    ) -> list[dict]:
        kova = func.date_bin(
            _ARALIK_GENISLIKLERI[aralik], OlcumTablosu.olcum_zamani, _KOVA_BASLANGICI
        ).label("zaman")
        ifade = (
            select(
                kova,
                func.avg(OlcumTablosu.doluluk_orani).label("ortalama_doluluk"),
                func.avg(OlcumTablosu.kisi_sayisi).label("ortalama_kisi"),
                func.count().label("olcum_sayisi"),
            )
            .where(
                OlcumTablosu.hat_id == hat_id,
                OlcumTablosu.olcum_zamani >= baslangic,
                OlcumTablosu.olcum_zamani <= bitis,
            )
            .group_by(kova)
            .order_by(kova)
        )
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.execute(ifade)).mappings().all()
        return [dict(s) for s in satirlar]

    async def hat_haftalik_oruntu(
        self, baslangic: datetime, bitis: datetime, min_olcum_sayisi: int = 5
    ) -> list[dict]:
        """hat_id × gun_no (0=Pazar..6=Cumartesi) × saat_dilimi(2 saatlik kova) →
        ortalama_doluluk, ortalama_kisi, olcum_sayisi. Az örneklemli kovalar elenir
        (min_olcum_sayisi) — LLM'e istatistiksel gürültü gitmesin diye.
        """
        gun_no = func.extract("dow", OlcumTablosu.olcum_zamani).cast(Integer).label("gun_no")
        saat_baslangic = (
            (func.extract("hour", OlcumTablosu.olcum_zamani).cast(Integer) / 2 * 2)
            .cast(Integer)
            .label("saat_baslangic")
        )
        ifade = (
            select(
                OlcumTablosu.hat_id,
                gun_no,
                saat_baslangic,
                func.avg(OlcumTablosu.doluluk_orani).label("ortalama_doluluk"),
                func.avg(OlcumTablosu.kisi_sayisi).label("ortalama_kisi"),
                func.count().label("olcum_sayisi"),
            )
            .where(
                OlcumTablosu.hat_id.is_not(None),
                OlcumTablosu.doluluk_orani.is_not(None),
                OlcumTablosu.olcum_zamani >= baslangic,
                OlcumTablosu.olcum_zamani <= bitis,
            )
            .group_by(OlcumTablosu.hat_id, gun_no, saat_baslangic)
            .having(func.count() >= min_olcum_sayisi)
            .order_by(OlcumTablosu.hat_id, gun_no, saat_baslangic)
        )
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.execute(ifade)).mappings().all()
        return [dict(s) for s in satirlar]

    async def hat_anlik_ozet(
        self, baslangic: datetime, bitis: datetime, min_olcum_sayisi: int = 3
    ) -> list[dict]:
        """hat_id → ortalama_doluluk, ortalama_kisi, olcum_sayisi (verilen pencerede, gün/saat
        kovası yok). "Yoğun" filtrelemesi burada yapılmaz; use-case katmanında
        seviye_belirle ile yapılır (bkz. app/application/uyari_uret.py).
        """
        ifade = (
            select(
                OlcumTablosu.hat_id,
                func.avg(OlcumTablosu.doluluk_orani).label("ortalama_doluluk"),
                func.avg(OlcumTablosu.kisi_sayisi).label("ortalama_kisi"),
                func.count().label("olcum_sayisi"),
            )
            .where(
                OlcumTablosu.hat_id.is_not(None),
                OlcumTablosu.doluluk_orani.is_not(None),
                OlcumTablosu.olcum_zamani >= baslangic,
                OlcumTablosu.olcum_zamani <= bitis,
            )
            .group_by(OlcumTablosu.hat_id)
            .having(func.count() >= min_olcum_sayisi)
            .order_by(OlcumTablosu.hat_id)
        )
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.execute(ifade)).mappings().all()
        return [dict(s) for s in satirlar]

    async def arac_olcumleri(
        self, arac_id: int, baslangic: datetime, bitis: datetime
    ) -> list[Olcum]:
        ifade = (
            select(OlcumTablosu)
            .where(
                OlcumTablosu.arac_id == arac_id,
                OlcumTablosu.olcum_zamani >= baslangic,
                OlcumTablosu.olcum_zamani <= bitis,
            )
            .order_by(OlcumTablosu.olcum_zamani)
        )
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.scalars(ifade)).all()
        return [
            Olcum(
                cihaz_id=s.cihaz_id,
                sira_no=s.sira_no,
                kisi_sayisi=s.kisi_sayisi,
                olcum_zamani=s.olcum_zamani,
                arac_id=s.arac_id,
                hat_id=s.hat_id,
                doluluk_orani=s.doluluk_orani,
                seviye=s.seviye,
            )
            for s in satirlar
        ]
