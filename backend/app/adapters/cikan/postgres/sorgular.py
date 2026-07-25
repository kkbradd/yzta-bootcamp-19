"""REST okuma uçlarının PostgreSQL sorguları (plan Bölüm 9).

Trend, ölçümleri denormalize hat_id kolonu üzerinden okur (Bölüm 8.1) —
zamansal join yok; gecikmeli ölçümler çekim damgalarıyla doğru kovaya düşer.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.cikan.postgres.tablolar import (
    CihazTablosu,
    DurakTablosu,
    GuzergahTablosu,
    HatAtamasiTablosu,
    HatDuraklariTablosu,
    HatTablosu,
    OlcumTablosu,
)
from app.domain.modeller import Cihaz, Durak, Guzergah, Hat, Olcum

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
        (min_olcum_sayisi) — LLM'e istatistiksel gürültü gitmesin diye. hat_no,
        LLM'in öneri metninde gerçek hat koduna (örn. "15A") referans verebilmesi
        için eklenir — Oneri domain modeline yazılmaz, yalnız LLM girdisidir.
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
                HatTablosu.hat_no,
                gun_no,
                saat_baslangic,
                func.avg(OlcumTablosu.doluluk_orani).label("ortalama_doluluk"),
                func.avg(OlcumTablosu.kisi_sayisi).label("ortalama_kisi"),
                func.count().label("olcum_sayisi"),
            )
            .join(HatTablosu, HatTablosu.id == OlcumTablosu.hat_id)
            .where(
                OlcumTablosu.hat_id.is_not(None),
                OlcumTablosu.doluluk_orani.is_not(None),
                OlcumTablosu.olcum_zamani >= baslangic,
                OlcumTablosu.olcum_zamani <= bitis,
            )
            .group_by(OlcumTablosu.hat_id, HatTablosu.hat_no, gun_no, saat_baslangic)
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
        seviye_belirle ile yapılır (bkz. app/application/uyari_uret.py). hat_no,
        LLM'in uyarı metninde gerçek hat koduna referans verebilmesi için eklenir.
        """
        ifade = (
            select(
                OlcumTablosu.hat_id,
                HatTablosu.hat_no,
                func.avg(OlcumTablosu.doluluk_orani).label("ortalama_doluluk"),
                func.avg(OlcumTablosu.kisi_sayisi).label("ortalama_kisi"),
                func.count().label("olcum_sayisi"),
            )
            .join(HatTablosu, HatTablosu.id == OlcumTablosu.hat_id)
            .where(
                OlcumTablosu.hat_id.is_not(None),
                OlcumTablosu.doluluk_orani.is_not(None),
                OlcumTablosu.olcum_zamani >= baslangic,
                OlcumTablosu.olcum_zamani <= bitis,
            )
            .group_by(OlcumTablosu.hat_id, HatTablosu.hat_no)
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

    async def duraklari_listele(self) -> list[Durak]:
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.scalars(select(DurakTablosu).order_by(DurakTablosu.id))).all()
        return [Durak(id=s.id, ad=s.ad, enlem=s.enlem, boylam=s.boylam) for s in satirlar]

    async def hat_duraklarini_listele(self, hat_id: int) -> list[Durak]:
        """Bir hattın duraklarını sıra numarasına göre döner."""
        ifade = (
            select(DurakTablosu)
            .join(HatDuraklariTablosu, HatDuraklariTablosu.durak_id == DurakTablosu.id)
            .where(HatDuraklariTablosu.hat_id == hat_id)
            .order_by(HatDuraklariTablosu.sira)
        )
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.scalars(ifade)).all()
        return [Durak(id=s.id, ad=s.ad, enlem=s.enlem, boylam=s.boylam) for s in satirlar]

    async def hat_durak_sayilarini_listele(self) -> dict[int, int]:
        """Her hat_id için durak sayısını döner (LinesPage 'DURAK SAYISI' kartı için)."""
        ifade = select(HatDuraklariTablosu.hat_id, func.count()).group_by(
            HatDuraklariTablosu.hat_id
        )
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.execute(ifade)).all()
        return dict(satirlar)

    async def hat_guzergahini_getir(self, hat_id: int) -> Guzergah | None:
        async with self._oturum_fabrikasi() as oturum:
            satir = await oturum.get(GuzergahTablosu, hat_id)
        if satir is None:
            return None
        return Guzergah(
            hat_id=satir.hat_id,
            koordinatlar=[tuple(nokta) for nokta in satir.koordinatlar],
            mesafe_metre=satir.mesafe_metre,
            sure_saniye=satir.sure_saniye,
        )

    async def aktif_hat_atamalarini_listele(self) -> list[tuple[int, int]]:
        """Güncel (bitis IS NULL) araç↔hat atamalarını (arac_id, hat_id) çiftleri olarak döner."""
        ifade = select(HatAtamasiTablosu.arac_id, HatAtamasiTablosu.hat_id).where(
            HatAtamasiTablosu.bitis.is_(None)
        )
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.execute(ifade)).all()
        return [(arac_id, hat_id) for arac_id, hat_id in satirlar]

    async def durak_hat_kodlarini_listele(self) -> dict[int, list[str]]:
        """Her durak_id için o duraktan geçen hatların kodlarını döner (aktarma bilgisi)."""
        ifade = (
            select(HatDuraklariTablosu.durak_id, HatTablosu.hat_no)
            .join(HatTablosu, HatTablosu.id == HatDuraklariTablosu.hat_id)
            .order_by(HatDuraklariTablosu.durak_id, HatTablosu.hat_no)
        )
        async with self._oturum_fabrikasi() as oturum:
            satirlar = (await oturum.execute(ifade)).all()
        sonuc: dict[int, list[str]] = {}
        for durak_id, hat_no in satirlar:
            sonuc.setdefault(durak_id, []).append(hat_no)
        return sonuc
