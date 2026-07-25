"""MQTT yayın sözleşmesi (docs/mqtt.md) — sapma sessiz veri kaybı demektir."""

import json
from datetime import UTC, datetime

import pytest

from app.yayinci import YAZILIM_SURUMU, Yayinci, vasiyet_olustur

CIHAZ_ID = "edge_0001"


class SahteIstemci:
    """aiomqtt.Client yerine geçer; yayınlananları olduğu gibi biriktirir."""

    def __init__(self):
        self.yayinlar = []

    async def publish(self, topic, payload, qos=0, retain=False):
        self.yayinlar.append({"topic": topic, "payload": payload, "qos": qos, "retain": retain})


@pytest.fixture
def istemci():
    return SahteIstemci()


@pytest.mark.asyncio
async def test_cevrimici_bildirimi_retained_yayinlanir(istemci):
    await Yayinci(CIHAZ_ID, istemci).cevrimici_bildir()

    (yayin,) = istemci.yayinlar
    assert yayin["topic"] == f"filo/{CIHAZ_ID}/durum"
    assert yayin["qos"] == 1
    # Retained olmalı: sonradan bağlanan backend cihazı çevrimiçi görebilsin.
    assert yayin["retain"] is True
    assert json.loads(yayin["payload"]) == {
        "cevrimici": True,
        "yazilim_surumu": YAZILIM_SURUMU,
    }


@pytest.mark.asyncio
async def test_olcum_sozlesmeye_uygun_yayinlanir(istemci):
    cekim = datetime(2026, 7, 19, 14, 22, 5, tzinfo=UTC)

    await Yayinci(CIHAZ_ID, istemci).olcum_yayinla(43, cekim)

    (yayin,) = istemci.yayinlar
    assert yayin["topic"] == f"filo/{CIHAZ_ID}/yogunluk"
    assert yayin["qos"] == 1
    # Yoğunluk mesajı retained OLMAMALI; yalnız durum mesajı kalıcıdır.
    assert yayin["retain"] is False

    olcum = json.loads(yayin["payload"])
    assert olcum["kisi_sayisi"] == 43
    # Alan adı 'timestamp' olmalı: 'olcum_zamani' yazılırsa backend doğrulamada düşürür.
    assert olcum["timestamp"] == "2026-07-19T14:22:05Z"


@pytest.mark.asyncio
async def test_sira_no_kesintisiz_artar(istemci):
    yayinci = Yayinci(CIHAZ_ID, istemci)
    cekim = datetime.now(UTC)

    for _ in range(3):
        await yayinci.olcum_yayinla(10, cekim)

    sira_numaralari = [json.loads(y["payload"])["sira_no"] for y in istemci.yayinlar]
    # Tekrar eden sira_no backend'de UNIQUE kısıtına takılıp sessizce yutulur.
    assert sira_numaralari == sorted(set(sira_numaralari))
    assert sira_numaralari[1] == sira_numaralari[0] + 1


@pytest.mark.asyncio
async def test_yeniden_baslatma_sira_nosunu_geri_almaz(istemci):
    """Sayaç duvar saatinden tohumlanır; yeniden başlatma mükerrer üretmemeli."""
    ilk = Yayinci(CIHAZ_ID, istemci)
    await ilk.olcum_yayinla(10, datetime.now(UTC))
    ilk_sira = json.loads(istemci.yayinlar[-1]["payload"])["sira_no"]

    await Yayinci(CIHAZ_ID, istemci).olcum_yayinla(10, datetime.now(UTC))
    ikinci_sira = json.loads(istemci.yayinlar[-1]["payload"])["sira_no"]

    assert ikinci_sira >= ilk_sira


def test_vasiyet_cihazi_cevrimdisi_ilan_eder():
    vasiyet = vasiyet_olustur(CIHAZ_ID)

    assert vasiyet.topic == f"filo/{CIHAZ_ID}/durum"
    assert vasiyet.qos == 1
    assert vasiyet.retain is True
    assert json.loads(vasiyet.payload) == {"cevrimici": False}
