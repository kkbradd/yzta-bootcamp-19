"""EventBus olaylarını SSE paketlerine çeviren saf yardımcılar.

FastAPI'den bağımsızdır: kuyruk köprüsü ve serileştirme burada izole test edilir.

Köprü neden gerekli: ``EventBus.publish`` abonelerini *yayınlayan thread'de*
senkron çağırır (core/events.py). ``OrchestratorAgent.run`` da senkron ve
bloklayıcıdır; bir worker thread'de koşarken olayları async üretece taşımanın
thread-güvenli yolu ``queue.Queue``dur.
"""

import json
import queue
from collections.abc import Callable
from typing import Any

from openjarvis.core.events import EventBus, EventType

from app.ayarlar import AZAMI_OLAY_BAYTI

# Kuyruk sonu nöbetçisi: ``None`` geçerli bir olay verisi olabildiği için
# ayrı bir tekil nesne kullanılır.
BITTI = object()

OLAY_HATA = "hata"
OLAY_BITTI = "bitti"


def kuyruga_abone_ol(bus: EventBus, kuyruk: queue.Queue) -> Callable[[], None]:
    """Tüm olay tiplerini kuyruğa aktarır; aboneliği kaldıran fonksiyon döner.

    ``subscribe`` tek bir tip alır (joker yok), bu yüzden 51 tipin hepsi tek tek
    bağlanır — ekranda hiçbir adım eksik kalmasın diye kasıtlı olarak filtresiz.
    """
    geri_cagirlar = {}
    for tip in EventType:
        geri_cagir = _kuyruga_yazan(kuyruk)
        geri_cagirlar[tip] = geri_cagir
        bus.subscribe(tip, geri_cagir)

    def abonelikleri_birak() -> None:
        for tip, geri_cagir in geri_cagirlar.items():
            bus.unsubscribe(tip, geri_cagir)

    return abonelikleri_birak


def _kuyruga_yazan(kuyruk: queue.Queue) -> Callable[[Any], None]:
    def yaz(olay: Any) -> None:
        kuyruk.put(olay)

    return yaz


def sse_paketi(ad: str, govde: str) -> str:
    """Tek bir SSE çerçevesi. `data` satır sonu içeremez; gövde JSON olmalı."""
    return f"event: {ad}\ndata: {govde}\n\n"


def olay_paketi(olay: Any) -> str:
    """EventBus olayını SSE çerçevesine çevirir."""
    return sse_paketi(olay.event_type.value, guvenli_govde(olay))


def guvenli_govde(olay: Any) -> str:
    """Olayı JSON'a çevirir; serileştirilemeyen tip veya aşırı boyut akışı öldürmez.

    ``default=str`` beklenmedik bir tip akışı kesmesin diye; ``ensure_ascii=False``
    Türkçe karakterler okunabilir kalsın diye. Boyut sınırı kendi savunmamızdır:
    ``inference_end.content`` yukarı akışta kırpılmıyor.
    """
    ham = {
        "zaman": olay.timestamp,
        "tip": olay.event_type.value,
        "veri": getattr(olay, "data", {}) or {},
    }
    govde = json.dumps(ham, ensure_ascii=False, default=str)
    if len(govde) <= AZAMI_OLAY_BAYTI:
        return govde
    return json.dumps(
        {"zaman": olay.timestamp, "tip": olay.event_type.value, "kirpildi": True},
        ensure_ascii=False,
    )


def bitti_paketi(cevap: Any) -> str:
    """Akışın sonunda nihai cevabı taşıyan çerçeve."""
    govde = json.dumps(
        {
            "cevap": cevap.cevap,
            "tur_sayisi": cevap.tur_sayisi,
            "arac_cagrilari": list(cevap.arac_cagrilari),
            "model": cevap.model,
        },
        ensure_ascii=False,
        default=str,
    )
    return sse_paketi(OLAY_BITTI, govde)


def hata_paketi(hata: BaseException) -> str:
    """Akış ortasında HTTP durum kodu değiştirilemez; hata da bir olaydır."""
    govde = json.dumps({"mesaj": str(hata) or type(hata).__name__}, ensure_ascii=False)
    return sse_paketi(OLAY_HATA, govde)
