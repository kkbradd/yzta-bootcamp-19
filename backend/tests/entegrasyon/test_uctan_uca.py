"""Uçtan uca entegrasyon testleri — compose ayaktayken çalışır (plan Faz 5).

Çalıştırma: docker compose up -d && python -m app.seed && uv run pytest tests/entegrasyon
Altyapı kapalıysa testler atlanır (birim testleri etkilemez, kabul kriteri #9).
"""

import asyncio
import json
import socket
import time
from datetime import UTC, datetime, timedelta

import aiomqtt
import httpx
import pytest
import websockets

API = "http://localhost:8000"
WS = "ws://localhost:8000/ws/canli"
BROKER_PORT = 1883


def _ayakta(port: int) -> bool:
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(
    not (_ayakta(8000) and _ayakta(BROKER_PORT)),
    reason="compose ayakta değil (docker compose up -d && python -m app.seed)",
)


async def _yayinla(topic: str, yuk: dict) -> None:
    async with aiomqtt.Client("localhost", port=BROKER_PORT) as istemci:
        await istemci.publish(topic, json.dumps(yuk), qos=1)


def _benzersiz_sira_no() -> int:
    return int(time.time() * 1000) % 1_000_000_000


async def _hat34_id(istemci: httpx.AsyncClient) -> int:
    hatlar = (await istemci.get(f"{API}/api/hatlar")).json()
    return next(h["hat_id"] for h in hatlar if h["hat_no"] == "34")


async def _sira_no_ile_olcumleri_bekle(
    istemci: httpx.AsyncClient, hat_id: int, sira_no: int
) -> list[dict]:
    """Hattaki TÜM araçların ölçümlerinde sira_no'yu polling ile arar.

    Hat 34'te birden fazla araç var ve ingest asenkron — belirli bir aracı
    varsaymak yerine sira_no (benzersiz) hepsinde aranır.
    """
    pencere = {
        "baslangic": (datetime.now(UTC) - timedelta(minutes=5)).isoformat(),
        "bitis": (datetime.now(UTC) + timedelta(minutes=5)).isoformat(),
    }
    for _ in range(30):
        anlik = (await istemci.get(f"{API}/api/hatlar/{hat_id}/anlik")).json()
        eslesenler = []
        for arac in anlik:
            olcumler = (
                await istemci.get(
                    f"{API}/api/araclar/{arac['arac_id']}/olcumler", params=pencere
                )
            ).json()
            eslesenler += [o for o in olcumler if o["sira_no"] == sira_no]
        if eslesenler:
            return eslesenler
        await asyncio.sleep(0.2)
    return []


async def test_saglik_tum_bagimliliklar_ok() -> None:
    async with httpx.AsyncClient() as istemci:
        yanit = await istemci.get(f"{API}/api/saglik")
    assert yanit.status_code == 200
    assert yanit.json()["bagimliliklar"] == {"postgres": "ok", "redis": "ok", "mqtt": "ok"}


async def test_olcum_yayini_zenginlesip_kaydedilir_ve_mukerrer_elenir() -> None:
    sira_no = _benzersiz_sira_no()
    yuk = {
        "sira_no": sira_no,
        "kisi_sayisi": 42,
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    await _yayinla("filo/edge_0001/yogunluk", yuk)
    await _yayinla("filo/edge_0001/yogunluk", yuk)  # mükerrer (QoS 1 taklidi)

    async with httpx.AsyncClient() as istemci:
        hat_id = await _hat34_id(istemci)
        eslesenler = await _sira_no_ile_olcumleri_bekle(istemci, hat_id, sira_no)

    assert len(eslesenler) == 1  # kabul kriteri #2: mükerrer publish tek satır
    assert eslesenler[0]["kisi_sayisi"] == 42
    assert eslesenler[0]["doluluk_orani"] is not None  # zenginleştirme çalıştı


async def test_ws_istemcisi_1_saniyede_arac_guncellemesi_alir() -> None:
    # Kabul kriteri #5: publish → WS istemcisine ≤1 sn'de arac_guncelleme düşer.
    sira_no = _benzersiz_sira_no()
    async with websockets.connect(WS) as ws:
        await _yayinla(
            "filo/edge_0001/yogunluk",
            {
                "sira_no": sira_no,
                "kisi_sayisi": 55,
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        baslangic = time.monotonic()
        while True:
            kalan = 1.0 - (time.monotonic() - baslangic)
            assert kalan > 0, "1 saniye içinde arac_guncelleme gelmedi"
            mesaj = json.loads(await asyncio.wait_for(ws.recv(), timeout=kalan))
            if mesaj["tip"] == "arac_guncelleme" and mesaj["kisi_sayisi"] == 55:
                assert mesaj["seviye"] is not None
                break


async def test_kayitsiz_cihaz_sistemi_dusurmez() -> None:
    # Kabul kriteri #6: bilinmeyen cihaz mesajı uyarıyla atlanır, servis ayakta kalır.
    await _yayinla(
        "filo/edge_9999/yogunluk",
        {
            "sira_no": _benzersiz_sira_no(),
            "kisi_sayisi": 5,
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )
    await asyncio.sleep(0.5)
    async with httpx.AsyncClient() as istemci:
        yanit = await istemci.get(f"{API}/api/saglik")
    assert yanit.status_code == 200


async def test_tunel_gecikmeli_olcumler_cekim_damgasindaki_kovaya_iner() -> None:
    # Kabul kriteri #3: tünelden boşalan geçmiş damgalı ölçümler, geldiği ana
    # değil çekim anındaki 15dk kovasına yerleşir.
    taban_sira = _benzersiz_sira_no()
    gecmis_damga = datetime.now(UTC) - timedelta(minutes=45)
    for kayma in range(3):  # 45, 40, 35 dk önce çekilmiş üç "birikmiş" ölçüm
        await _yayinla(
            "filo/edge_0001/yogunluk",
            {
                "sira_no": taban_sira + kayma,
                "kisi_sayisi": 30 + kayma,
                "timestamp": (gecmis_damga + timedelta(minutes=5 * kayma)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
            },
        )
    await asyncio.sleep(1.0)

    async with httpx.AsyncClient() as istemci:
        hatlar = (await istemci.get(f"{API}/api/hatlar")).json()
        hat_id = next(h["hat_id"] for h in hatlar if h["hat_no"] == "34")
        trend = (
            await istemci.get(
                f"{API}/api/hatlar/{hat_id}/trend",
                params={
                    "baslangic": (gecmis_damga - timedelta(minutes=5)).isoformat(),
                    "bitis": (gecmis_damga + timedelta(minutes=15)).isoformat(),
                    "aralik": "15dk",
                },
            )
        ).json()

    # 45-35 dk önceki pencerede en az iki dolu kova olmalı (5 dk arayla üç ölçüm).
    assert sum(nokta["olcum_sayisi"] for nokta in trend) >= 3
