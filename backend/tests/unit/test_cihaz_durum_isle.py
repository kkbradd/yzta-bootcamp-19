"""CihazDurumIsleyici birim testleri — sahte adaptörlerle, container'sız."""

from datetime import UTC, datetime

from app.application.cihaz_durum_isle import CihazDurumIsleyici

SIMDI = datetime(2026, 7, 8, 14, 35, 12, tzinfo=UTC)


class SahteAnlikDurum:
    def __init__(self) -> None:
        self.cihaz_yazimlari: list[tuple] = []

    async def arac_durumunu_yaz(self, olcum) -> None:  # pragma: no cover - kullanılmaz
        raise AssertionError("bu senaryoda çağrılmamalı")

    async def cihaz_durumunu_yaz(
        self, cihaz_id: str, cevrimici: bool, yazilim_surumu: str | None, son_gorulme
    ) -> None:
        self.cihaz_yazimlari.append((cihaz_id, cevrimici, yazilim_surumu, son_gorulme))


class SahteYayin:
    def __init__(self) -> None:
        self.cihaz_durumlari: list[tuple] = []

    async def arac_guncellemesini_yayinla(self, olcum) -> None:  # pragma: no cover
        raise AssertionError("bu senaryoda çağrılmamalı")

    async def cihaz_durumunu_yayinla(self, cihaz_id: str, cevrimici: bool, son_gorulme) -> None:
        self.cihaz_durumlari.append((cihaz_id, cevrimici, son_gorulme))


async def test_durum_yazilir_ve_yayinlanir() -> None:
    anlik, yayin = SahteAnlikDurum(), SahteYayin()
    isleyici = CihazDurumIsleyici(anlik_durum=anlik, canli_yayin=yayin)

    await isleyici.isle("edge_0042", cevrimici=True, yazilim_surumu="1.2.0", son_gorulme=SIMDI)

    assert anlik.cihaz_yazimlari == [("edge_0042", True, "1.2.0", SIMDI)]
    assert yayin.cihaz_durumlari == [("edge_0042", True, SIMDI)]


async def test_retained_tekrarinda_son_gorulme_none_gecirilir() -> None:
    # son_gorulme=None sözleşmesi: mevcut değer korunur (adaptör sorumluluğu).
    anlik, yayin = SahteAnlikDurum(), SahteYayin()
    isleyici = CihazDurumIsleyici(anlik_durum=anlik, canli_yayin=yayin)

    await isleyici.isle("edge_0042", cevrimici=False, yazilim_surumu=None, son_gorulme=None)

    assert anlik.cihaz_yazimlari == [("edge_0042", False, None, None)]
    assert yayin.cihaz_durumlari == [("edge_0042", False, None)]
