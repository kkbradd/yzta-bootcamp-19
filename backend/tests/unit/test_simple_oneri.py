"""SimpleOneriUreticisi birim testleri — SahteMotor ile, Ollama/ağ gerektirmez.

Gemini üreticisiyle aynı sözleşme: özet → LLM → Oneri listesi; LLM'in uydurduğu
hat/gün/saat atlanır; boş özet → boş liste; markdown fence'li çıktı ayrıştırılır.
"""

import json
from typing import Any

from app.adapters.cikan.simple_oneri import SimpleOneriUreticisi
from app.domain.modeller import Oneri

OZET = [
    {"hat_id": 1, "gun_no": 1, "saat_baslangic": 8, "saat_bitis": 10,
     "ortalama_doluluk": 0.89, "karsilastirma_ortalama_doluluk": 0.42},
]

# SimpleAgent'ın döndürdüğü ham içerik (küçük model markdown fence sarar).
_TAM_YANIT = (
    '```json\n{"oneriler": [{"hat_id": 1, "gun_no": 1, "saat_baslangic": 8, '
    '"saat_bitis": 10, "oneri_metni": "Ek sefer düşünün", "gerekce": "Sabah yoğun"}]}\n```'
)
_UYDURMA_YANIT = (
    '{"oneriler": [{"hat_id": 99, "gun_no": 3, "saat_baslangic": 14, '
    '"saat_bitis": 16, "oneri_metni": "x", "gerekce": "y"}]}'
)


class SahteMotor:
    """SimpleAgent'ın çağırdığı motoru taklit eder; sabit içerik döndürür."""

    def __init__(self, icerik: str) -> None:
        self._icerik = icerik
        self.cagrilar: list[dict[str, Any]] = []

    def generate(self, messages: list[Any], **kwargs: Any) -> dict[str, Any]:
        self.cagrilar.append({"mesajlar": list(messages), **kwargs})
        return {"content": self._icerik, "tool_calls": []}


def _uretici(icerik: str) -> tuple[SimpleOneriUreticisi, SahteMotor]:
    motor = SahteMotor(icerik)
    return SimpleOneriUreticisi(motor=motor, model="test-model"), motor


async def test_bos_ozet_llm_cagrilmadan_bos_doner():
    uretici, motor = _uretici(_TAM_YANIT)

    sonuc = await uretici.uret([])

    assert sonuc == []
    assert motor.cagrilar == []


async def test_fenceli_yanit_ayristirilir_ve_oneri_doner():
    uretici, _ = _uretici(_TAM_YANIT)

    sonuc = await uretici.uret(OZET)

    assert len(sonuc) == 1
    assert isinstance(sonuc[0], Oneri)
    assert sonuc[0].hat_id == 1
    assert sonuc[0].oneri_metni == "Ek sefer düşünün"


async def test_orijinal_veriden_doluluk_alinir():
    uretici, _ = _uretici(_TAM_YANIT)

    sonuc = await uretici.uret(OZET)

    assert sonuc[0].ortalama_doluluk == 0.89
    assert sonuc[0].karsilastirma_ortalama_doluluk == 0.42


async def test_llm_uydurma_hat_uretirse_atlanir():
    uretici, _ = _uretici(_UYDURMA_YANIT)

    sonuc = await uretici.uret(OZET)

    assert sonuc == []


async def test_sistem_promptu_ve_ozet_motora_gider():
    uretici, motor = _uretici(_TAM_YANIT)

    await uretici.uret(OZET)

    gonderilen = json.dumps(motor.cagrilar[0], default=str)
    assert "operasyon analisti" in gonderilen
    assert "0.89" in gonderilen
