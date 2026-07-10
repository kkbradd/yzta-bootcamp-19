"""WebSocket yayın yöneticisinin birim testleri — gerçek soket gerektirmez.

Mesaj sözleşmesi (plan Bölüm 8.5/9): başarılı ölçümde tüm bağlı istemcilere
{"tip": "arac_guncelleme", ...}; durum değişiminde {"tip": "cihaz_durum", ...}.
Kopan istemci yayını bozmaz, sessizce düşürülür.
"""

from datetime import UTC, datetime

from app.adapters.cikan.ws_yayin import BaglantiYoneticisi
from app.domain.modeller import Olcum

SIMDI = datetime(2026, 7, 8, 14, 35, 12, tzinfo=UTC)

OLCUM = Olcum(
    cihaz_id="edge_0042",
    sira_no=18452,
    kisi_sayisi=23,
    olcum_zamani=SIMDI,
    arac_id=7,
    hat_id=3,
    doluluk_orani=0.766,
    seviye="yogun",
)


class SahteWebSocket:
    def __init__(self, patlasin: bool = False) -> None:
        self.patlasin = patlasin
        self.kabul_edildi = False
        self.mesajlar: list[dict] = []

    async def accept(self) -> None:
        self.kabul_edildi = True

    async def send_json(self, mesaj: dict) -> None:
        if self.patlasin:
            raise RuntimeError("bağlantı koptu")
        self.mesajlar.append(mesaj)


async def test_arac_guncellemesi_tum_istemcilere_gider() -> None:
    yonetici = BaglantiYoneticisi()
    birinci, ikinci = SahteWebSocket(), SahteWebSocket()
    await yonetici.baglan(birinci)
    await yonetici.baglan(ikinci)

    await yonetici.arac_guncellemesini_yayinla(OLCUM)

    for istemci in (birinci, ikinci):
        assert istemci.kabul_edildi
        (mesaj,) = istemci.mesajlar
        assert mesaj["tip"] == "arac_guncelleme"
        assert mesaj["arac_id"] == 7
        assert mesaj["hat_id"] == 3
        assert mesaj["kisi_sayisi"] == 23
        assert mesaj["doluluk_orani"] == 0.766
        assert mesaj["seviye"] == "yogun"
        assert mesaj["zaman"] == SIMDI.isoformat()


async def test_kopan_istemci_yayini_bozmaz_ve_dusurulur() -> None:
    yonetici = BaglantiYoneticisi()
    saglam, kopuk = SahteWebSocket(), SahteWebSocket(patlasin=True)
    await yonetici.baglan(kopuk)
    await yonetici.baglan(saglam)

    await yonetici.arac_guncellemesini_yayinla(OLCUM)
    await yonetici.arac_guncellemesini_yayinla(OLCUM)

    assert len(saglam.mesajlar) == 2
    assert yonetici.baglanti_sayisi == 1  # kopuk istemci ilk hatada düşürüldü


async def test_cihaz_durumu_yayinlanir() -> None:
    yonetici = BaglantiYoneticisi()
    istemci = SahteWebSocket()
    await yonetici.baglan(istemci)

    await yonetici.cihaz_durumunu_yayinla("edge_0042", cevrimici=False, son_gorulme=SIMDI)

    (mesaj,) = istemci.mesajlar
    assert mesaj == {
        "tip": "cihaz_durum",
        "cihaz_id": "edge_0042",
        "cevrimici": False,
        "son_gorulme": SIMDI.isoformat(),
    }


async def test_kopar_sonrasi_istemci_mesaj_almaz() -> None:
    yonetici = BaglantiYoneticisi()
    istemci = SahteWebSocket()
    await yonetici.baglan(istemci)
    yonetici.kopar(istemci)

    await yonetici.arac_guncellemesini_yayinla(OLCUM)

    assert istemci.mesajlar == []
    assert yonetici.baglanti_sayisi == 0
