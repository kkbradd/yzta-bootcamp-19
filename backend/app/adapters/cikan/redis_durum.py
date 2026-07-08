"""AnlikDurumPort'un Redis implementasyonu + REST okuma yüzeyi (plan Bölüm 8.3-8.4).

Anahtar şeması sözleşmesi:
  HSET   arac:{arac_id}:durum   kisi_sayisi .. doluluk .. seviye .. zaman ..   (TTL 30 sn)
  HSET   hat:{hat_id}:araclar   {arac_id} {doluluk}                            (TTL 60 sn)
  ZADD   hatlar:doluluk         {ortalama} hat:{hat_id}
  HSET   cihaz:{id}:durum       cevrimici .. son_gorulme .. yazilim_surumu ..  (TTL yok)

Değişmez: arac_durumunu_yaz yalnız araç ölçümüyle çağrılır (bkz. AnlikDurumPort);
o dalda doluluk_orani ve seviye her zaman doludur — fallback gerekmez.
"""

from dataclasses import dataclass
from datetime import datetime
from statistics import fmean

from redis.asyncio import Redis

from app.domain.modeller import Olcum


@dataclass(frozen=True, slots=True)
class AracAnlik:
    kisi_sayisi: int
    doluluk_orani: float
    seviye: str
    zaman: datetime


@dataclass(frozen=True, slots=True)
class CihazAnlik:
    cevrimici: bool
    son_gorulme: datetime | None
    yazilim_surumu: str | None


class RedisAnlikDurum:
    def __init__(self, redis: Redis, arac_ttl_sn: int, hat_ttl_sn: int) -> None:
        self._redis = redis
        self._arac_ttl_sn = arac_ttl_sn
        self._hat_ttl_sn = hat_ttl_sn

    # ---- yazma (AnlikDurumPort) ----

    async def arac_durumunu_yaz(self, olcum: Olcum) -> None:
        arac_anahtari = f"arac:{olcum.arac_id}:durum"
        boru = self._redis.pipeline()
        boru.hset(
            arac_anahtari,
            mapping={
                "kisi_sayisi": olcum.kisi_sayisi,
                "doluluk": olcum.doluluk_orani,
                "seviye": olcum.seviye,
                "zaman": olcum.olcum_zamani.isoformat(),
            },
        )
        boru.expire(arac_anahtari, self._arac_ttl_sn)
        if olcum.hat_id is None:
            await boru.execute()
            return

        hat_anahtari = f"hat:{olcum.hat_id}:araclar"
        boru.hset(hat_anahtari, str(olcum.arac_id), str(olcum.doluluk_orani))
        boru.expire(hat_anahtari, self._hat_ttl_sn)
        await boru.execute()

        ortalama, _ = await self.hat_ozeti(olcum.hat_id)
        if ortalama is not None:
            await self._redis.zadd("hatlar:doluluk", {f"hat:{olcum.hat_id}": ortalama})

    async def cihaz_durumunu_yaz(
        self,
        cihaz_id: str,
        cevrimici: bool,
        yazilim_surumu: str | None,
        son_gorulme: datetime | None,
    ) -> None:
        alanlar: dict[str, str] = {"cevrimici": "1" if cevrimici else "0"}
        if son_gorulme is not None:  # None = retained tekrar oynatma; mevcut damga korunur
            alanlar["son_gorulme"] = son_gorulme.isoformat()
        if yazilim_surumu is not None:  # cihazın bildirdiği güncel sürüm
            alanlar["yazilim_surumu"] = yazilim_surumu
        await self._redis.hset(f"cihaz:{cihaz_id}:durum", mapping=alanlar)

    # ---- okuma (REST uçları için) ----

    async def hat_arac_doluluklari(self, hat_id: int) -> dict[int, float]:
        ham = await self._redis.hgetall(f"hat:{hat_id}:araclar")
        return {int(arac_id): float(doluluk) for arac_id, doluluk in ham.items()}

    async def hat_ozeti(self, hat_id: int) -> tuple[float | None, int]:
        """Hat ortalaması = HVALS ortalaması (plan 8.3) — tek kanonik hesap noktası."""
        doluluklar = await self.hat_arac_doluluklari(hat_id)
        if not doluluklar:
            return None, 0
        return fmean(doluluklar.values()), len(doluluklar)

    async def arac_durumu(self, arac_id: int) -> AracAnlik | None:
        ham = await self._redis.hgetall(f"arac:{arac_id}:durum")
        if not ham:
            return None
        return AracAnlik(
            kisi_sayisi=int(ham[b"kisi_sayisi"]),
            doluluk_orani=float(ham[b"doluluk"]),
            seviye=ham[b"seviye"].decode(),
            zaman=datetime.fromisoformat(ham[b"zaman"].decode()),
        )

    async def cihaz_durumu(self, cihaz_id: str) -> CihazAnlik | None:
        ham = await self._redis.hgetall(f"cihaz:{cihaz_id}:durum")
        if not ham:
            return None
        son_gorulme_ham = ham.get(b"son_gorulme")
        surum_ham = ham.get(b"yazilim_surumu")
        return CihazAnlik(
            cevrimici=ham[b"cevrimici"] == b"1",
            son_gorulme=(
                datetime.fromisoformat(son_gorulme_ham.decode()) if son_gorulme_ham else None
            ),
            yazilim_surumu=surum_ham.decode() if surum_ham else None,
        )
