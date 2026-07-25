"""Akış yardımcıları: serileştirme, kırpma, abonelik temizliği."""

import json
import queue
from dataclasses import dataclass
from typing import Any

from openjarvis.core.events import EventBus, EventType

from app.akis import (
    BITTI,
    bitti_paketi,
    guvenli_govde,
    hata_paketi,
    kuyruga_abone_ol,
    olay_paketi,
    sse_paketi,
)
from app.ayarlar import AZAMI_OLAY_BAYTI
from app.cekirdek import AsistanCevabi


@dataclass
class SahteOlay:
    event_type: Any
    timestamp: float
    data: dict


def _olay(veri: dict) -> SahteOlay:
    return SahteOlay(event_type=EventType.TOOL_CALL_END, timestamp=1.5, data=veri)


def test_govde_tek_satir_olur():
    """SSE `data:` alanı satır sonu içeremez; JSON kaçırması buna güvence."""
    govde = guvenli_govde(_olay({"result": "birinci\nikinci"}))

    assert "\n" not in govde
    assert json.loads(govde)["veri"]["result"] == "birinci\nikinci"


def test_turkce_karakterler_okunabilir_kalir():
    govde = guvenli_govde(_olay({"result": "Üsküdar – Ümraniye"}))

    assert "Üsküdar" in govde  # ensure_ascii=False


def test_serilestirilemeyen_tip_akisi_oldurmez():
    """default=str olmasaydı tek bir garip tip tüm akışı keserdi."""
    govde = guvenli_govde(_olay({"nesne": object()}))

    assert json.loads(govde)["veri"]["nesne"].startswith("<object")


def test_asiri_buyuk_olay_kirpilir():
    govde = guvenli_govde(_olay({"result": "x" * (AZAMI_OLAY_BAYTI + 100)}))

    assert len(govde) < AZAMI_OLAY_BAYTI
    assert json.loads(govde)["kirpildi"] is True


def test_olay_paketi_tipi_ad_olarak_kullanir():
    paket = olay_paketi(_olay({"tool": "hat_yogunluklari"}))

    assert paket.startswith("event: tool_call_end\ndata: ")
    assert paket.endswith("\n\n")


def test_bitti_paketi_nihai_cevabi_tasir():
    cevap = AsistanCevabi(
        cevap="15E yoğun", tur_sayisi=2, arac_cagrilari=["hat_yogunluklari"], model="qwen"
    )

    paket = bitti_paketi(cevap)

    assert paket.startswith("event: bitti\n")
    govde = json.loads(paket.split("data: ", 1)[1].strip())
    assert govde["cevap"] == "15E yoğun"
    assert govde["arac_cagrilari"] == ["hat_yogunluklari"]


def test_hata_paketi_mesaji_tasir():
    paket = hata_paketi(RuntimeError("motor kapalı"))

    assert paket.startswith("event: hata\n")
    assert json.loads(paket.split("data: ", 1)[1].strip())["mesaj"] == "motor kapalı"


def test_mesajsiz_hata_tip_adini_kullanir():
    """Boş mesajlı istisnada kullanıcı en azından hata türünü görsün."""
    paket = hata_paketi(ValueError())

    assert json.loads(paket.split("data: ", 1)[1].strip())["mesaj"] == "ValueError"


def test_sse_paketi_bicimi():
    assert sse_paketi("bitti", "{}") == "event: bitti\ndata: {}\n\n"


def test_tum_olaylar_kuyruga_dusar():
    bus = EventBus()
    kuyruk: queue.Queue = queue.Queue()
    kuyruga_abone_ol(bus, kuyruk)

    bus.publish(EventType.AGENT_TURN_START, {"agent": "orchestrator"})
    bus.publish(EventType.TOOL_CALL_START, {"tool": "hat_trend"})

    assert kuyruk.get_nowait().event_type is EventType.AGENT_TURN_START
    assert kuyruk.get_nowait().event_type is EventType.TOOL_CALL_START


def test_abonelik_birakilinca_olay_akmaz():
    """Sızıntı olmamalı: istek bitince kuyruğa yazılmaya devam edilmemeli."""
    bus = EventBus()
    kuyruk: queue.Queue = queue.Queue()
    birak = kuyruga_abone_ol(bus, kuyruk)

    birak()
    bus.publish(EventType.AGENT_TURN_END, {"turns": 1})

    assert kuyruk.empty()


def test_bitti_nobetcisi_none_ile_karismaz():
    """None geçerli bir olay verisi olabildiği için nöbetçi ayrı bir nesnedir."""
    assert BITTI is not None
