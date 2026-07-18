"""SimpleUyariUreticisi birim testleri — SahteMotor ile, Ollama/ağ gerektirmez."""

from typing import Any

from app.adapters.cikan.simple_uyari import SimpleUyariUreticisi
from app.domain.modeller import Uyari

OZET = [
    {"hat_id": 1, "ortalama_doluluk": 0.82, "ortalama_kisi": 71.0},
]

_TAM_YANIT = (
    '```json\n{"uyarilar": [{"hat_id": 1, "uyari_metni": "Ek sefer değerlendirilebilir", '
    '"gerekce": "Son saatlerde yoğun"}]}\n```'
)
_UYDURMA_YANIT = '{"uyarilar": [{"hat_id": 77, "uyari_metni": "x", "gerekce": "y"}]}'


class SahteMotor:
    def __init__(self, icerik: str) -> None:
        self._icerik = icerik
        self.cagrilar: list[dict[str, Any]] = []

    def generate(self, messages: list[Any], **kwargs: Any) -> dict[str, Any]:
        self.cagrilar.append({"mesajlar": list(messages), **kwargs})
        return {"content": self._icerik, "tool_calls": []}


def _uretici(icerik: str) -> tuple[SimpleUyariUreticisi, SahteMotor]:
    motor = SahteMotor(icerik)
    return SimpleUyariUreticisi(motor=motor, model="test-model"), motor


async def test_bos_ozet_llm_cagrilmadan_bos_doner():
    uretici, motor = _uretici(_TAM_YANIT)

    sonuc = await uretici.uret([])

    assert sonuc == []
    assert motor.cagrilar == []


async def test_fenceli_yanit_ayristirilir_ve_uyari_doner():
    uretici, _ = _uretici(_TAM_YANIT)

    sonuc = await uretici.uret(OZET)

    assert len(sonuc) == 1
    assert isinstance(sonuc[0], Uyari)
    assert sonuc[0].hat_id == 1
    assert sonuc[0].ortalama_kisi == 71.0


async def test_llm_uydurma_hat_uretirse_atlanir():
    uretici, _ = _uretici(_UYDURMA_YANIT)

    sonuc = await uretici.uret(OZET)

    assert sonuc == []
