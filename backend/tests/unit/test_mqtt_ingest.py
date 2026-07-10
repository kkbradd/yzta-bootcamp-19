"""MqttIngest mesaj işleme sınırlarının birim testleri — broker gerektirmez.

Politika (plan Bölüm 7-8 + thermo Faz 2 bulgusu): parse/doğrulama hatası =
bozuk mesaj → logla, düşür; işleme (dispatch) hatası = beklenmeyen → logla,
akış DURMAZ. Retained durum mesajı son_gorulme'yi tazelemez.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.adapters.giren.mqtt_ingest import MqttIngest
from app.ayarlar import Ayarlar


@dataclass
class SahteTopic:
    value: str


@dataclass
class SahteMesaj:
    topic: SahteTopic
    payload: bytes
    retain: bool = False


@dataclass
class SahteOlcumIsleyici:
    cagrilar: list[dict] = field(default_factory=list)
    patlasin: bool = False

    async def isle(self, **kwargs) -> None:
        if self.patlasin:
            raise RuntimeError("veritabanı koptu")
        self.cagrilar.append(kwargs)


@dataclass
class SahteCihazDurumIsleyici:
    cagrilar: list[dict] = field(default_factory=list)

    async def isle(self, **kwargs) -> None:
        self.cagrilar.append(kwargs)


def _ingest_kur(
    patlasin: bool = False,
) -> tuple[MqttIngest, SahteOlcumIsleyici, SahteCihazDurumIsleyici]:
    olcum = SahteOlcumIsleyici(patlasin=patlasin)
    durum = SahteCihazDurumIsleyici()
    return MqttIngest(Ayarlar(), olcum, durum), olcum, durum


def _yogunluk_mesaji(icerik: bytes, cihaz_id: str = "edge_0042") -> SahteMesaj:
    return SahteMesaj(topic=SahteTopic(f"filo/{cihaz_id}/yogunluk"), payload=icerik)


async def test_gecerli_yogunluk_mesaji_use_caseye_ulasir() -> None:
    ingest, olcum, _ = _ingest_kur()
    yuk = b'{"sira_no": 1, "kisi_sayisi": 23, "timestamp": "2026-07-08T14:35:12Z"}'

    await ingest._mesaji_isle(_yogunluk_mesaji(yuk))

    assert olcum.cagrilar == [
        {
            "cihaz_id": "edge_0042",
            "sira_no": 1,
            "kisi_sayisi": 23,
            "olcum_zamani": datetime(2026, 7, 8, 14, 35, 12, tzinfo=UTC),
        }
    ]


async def test_bozuk_json_dusurulur_islenmez() -> None:
    ingest, olcum, durum = _ingest_kur()

    await ingest._mesaji_isle(_yogunluk_mesaji(b"bozuk json"))

    assert olcum.cagrilar == [] and durum.cagrilar == []


async def test_eksik_alanli_mesaj_dusurulur() -> None:
    ingest, olcum, _ = _ingest_kur()

    await ingest._mesaji_isle(_yogunluk_mesaji(b'{"sira_no": 1}'))

    assert olcum.cagrilar == []


async def test_isleme_hatasi_akisi_durdurmaz() -> None:
    # PG kopması gibi beklenmeyen bir hata mesaj döngüsünü öldürmemeli.
    ingest, _, _ = _ingest_kur(patlasin=True)
    yuk = b'{"sira_no": 1, "kisi_sayisi": 23, "timestamp": "2026-07-08T14:35:12Z"}'

    await ingest._mesaji_isle(_yogunluk_mesaji(yuk))  # istisna yükselMEmeli


async def test_durum_mesaji_son_gorulmeyi_gunceller() -> None:
    ingest, _, durum = _ingest_kur()
    mesaj = SahteMesaj(
        topic=SahteTopic("filo/edge_0042/durum"),
        payload=b'{"cevrimici": true, "yazilim_surumu": "1.2.0"}',
    )

    await ingest._mesaji_isle(mesaj)

    (cagri,) = durum.cagrilar
    assert cagri["cihaz_id"] == "edge_0042"
    assert cagri["cevrimici"] is True
    assert cagri["son_gorulme"] is not None


async def test_retained_durum_mesaji_son_gorulmeyi_tazelemez() -> None:
    # Broker, yeniden bağlanan aboneye retained durum mesajını tekrar oynatır;
    # bu tekrar "cihaz şimdi görüldü" anlamına gelmez.
    ingest, _, durum = _ingest_kur()
    mesaj = SahteMesaj(
        topic=SahteTopic("filo/edge_0042/durum"),
        payload=b'{"cevrimici": true}',
        retain=True,
    )

    await ingest._mesaji_isle(mesaj)

    (cagri,) = durum.cagrilar
    assert cagri["cevrimici"] is True
    assert cagri["son_gorulme"] is None  # mevcut değer korunur
