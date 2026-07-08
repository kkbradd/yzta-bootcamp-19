"""Geçici bellek içi adaptörler — Faz 3 (Redis) ve Faz 4 (WebSocket) gelene dek
kompozisyon kökünün ihtiyaç duyduğu port implementasyonları.

Faz 3'te BellekIciAnlikDurum → RedisAnlikDurum, Faz 4'te SessizYayin →
WebSocketYayini ile değiştirilecek; bu dosya o noktada silinecek.
"""

from datetime import datetime

from app.domain.modeller import Olcum


class BellekIciAnlikDurum:
    """AnlikDurumPort implementasyonu — süreç içi sözlükler, TTL yok."""

    def __init__(self) -> None:
        self.arac_durumlari: dict[int, Olcum] = {}
        self.cihaz_durumlari: dict[str, tuple[bool, str | None, datetime | None]] = {}

    async def arac_durumunu_yaz(self, olcum: Olcum) -> None:
        if olcum.arac_id is not None:
            self.arac_durumlari[olcum.arac_id] = olcum

    async def cihaz_durumunu_yaz(
        self,
        cihaz_id: str,
        cevrimici: bool,
        yazilim_surumu: str | None,
        son_gorulme: datetime | None,
    ) -> None:
        if son_gorulme is None:  # retained tekrar oynatma: mevcut damga korunur
            onceki = self.cihaz_durumlari.get(cihaz_id)
            son_gorulme = onceki[2] if onceki else None
        self.cihaz_durumlari[cihaz_id] = (cevrimici, yazilim_surumu, son_gorulme)


class SessizYayin:
    """CanliYayinPort implementasyonu — Faz 4'e kadar yayın yok (no-op)."""

    async def arac_guncellemesini_yayinla(self, olcum: Olcum) -> None:
        return None

    async def cihaz_durumunu_yayinla(
        self, cihaz_id: str, cevrimici: bool, son_gorulme: datetime | None
    ) -> None:
        return None
