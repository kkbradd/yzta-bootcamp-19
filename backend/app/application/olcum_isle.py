"""Ölçüm işleme hattı (plan Bölüm 8):
zenginleştir → seviye hesapla → depoya yaz (dedup yazma anında UNIQUE +
ON CONFLICT ile) → anlık durumu güncelle → yayınla.

Zenginleştirme çekim damgasına göre yapılır: gecikmeli (tünel) mesaj, geldiği
andaki değil ölçüm anındaki atamaya işlenir; çözülen arac_id/hat_id kayda
denormalize edilir (tarihsel doğruluk).
"""

import logging
from dataclasses import dataclass
from datetime import datetime

from app.domain.modeller import Olcum
from app.domain.seviye import doluluk_orani_hesapla, seviye_belirle
from app.ports.anlik_durum import AnlikDurumPort
from app.ports.canli_yayin import CanliYayinPort
from app.ports.depolar import AtamaDeposuPort, OlcumDeposuPort

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SeviyeEsikleri:
    seyrek_ust: float
    orta_ust: float


@dataclass(frozen=True, slots=True)
class OlcumIsleyici:
    olcum_deposu: OlcumDeposuPort
    atama_deposu: AtamaDeposuPort
    anlik_durum: AnlikDurumPort
    canli_yayin: CanliYayinPort
    esikler: SeviyeEsikleri

    async def isle(
        self, cihaz_id: str, sira_no: int, kisi_sayisi: int, olcum_zamani: datetime
    ) -> Olcum | None:
        """Tek ölçümü uçtan uca işler; işlenmediyse (kayıtsız/mükerrer) None döner."""
        olcum = await self._zenginlestir(cihaz_id, sira_no, kisi_sayisi, olcum_zamani)
        if olcum is None:
            return None

        eklendi = await self.olcum_deposu.ekle(olcum)
        if not eklendi:
            logger.info("mükerrer ölçüm atlandı cihaz_id=%s sira_no=%s", cihaz_id, sira_no)
            return None

        if olcum.arac_id is not None:
            await self.anlik_durum.arac_durumunu_yaz(olcum)
            await self.canli_yayin.arac_guncellemesini_yayinla(olcum)
        return olcum

    async def _zenginlestir(
        self, cihaz_id: str, sira_no: int, kisi_sayisi: int, olcum_zamani: datetime
    ) -> Olcum | None:
        """Cihazı çekim anındaki atamasına göre araca/durağa ve hatta bağlar."""
        atama = await self.atama_deposu.cihaz_atamasini_bul(cihaz_id, olcum_zamani)
        if atama is None:
            logger.warning("kayıtsız cihaz, mesaj atlandı cihaz_id=%s", cihaz_id)
            return None

        if atama.arac_id is None:
            # Durak cihazı: kapasite yok → yalnız sayı saklanır (plan 8.2).
            return Olcum(
                cihaz_id=cihaz_id,
                sira_no=sira_no,
                kisi_sayisi=kisi_sayisi,
                olcum_zamani=olcum_zamani,
            )

        arac = await self.atama_deposu.arac_getir(atama.arac_id)
        if arac is None:
            logger.warning(
                "atama araç kaydına çözülemedi cihaz_id=%s arac_id=%s", cihaz_id, atama.arac_id
            )
            return None

        hat_atamasi = await self.atama_deposu.hat_atamasini_bul(arac.id, olcum_zamani)
        oran = doluluk_orani_hesapla(kisi_sayisi, arac.kapasite)
        return Olcum(
            cihaz_id=cihaz_id,
            sira_no=sira_no,
            kisi_sayisi=kisi_sayisi,
            olcum_zamani=olcum_zamani,
            arac_id=arac.id,
            hat_id=hat_atamasi.hat_id if hat_atamasi else None,
            doluluk_orani=oran,
            seviye=seviye_belirle(oran, self.esikler.seyrek_ust, self.esikler.orta_ust),
        )
