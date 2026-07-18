"""Üretici fabrikası + fallback birim testleri — motor seçimi ve gizlilik yönü.

Kritik kurallar:
- AI_MOTOR=local → yerel üretici; =gemini + anahtar → Gemini üretici.
- gemini + anahtarsız → AyarHatasi (servis çökmesin, açık hata versin).
- Fallback ASİMETRİK: gemini düşerse local'e düşer (güvenli); local düşerse
  gemini'ye DÜŞMEZ — "lokal iste" diyenin verisi Google'a sızmaz.
"""

from typing import Any

import pytest

from app.adapters.cikan._fallback import FallbackUretici
from app.adapters.cikan._uretici_fabrika import AyarHatasi, oneri_ureticisi_sec


class SahteAyarlar:
    def __init__(self, ai_motor: str, gemini_api_key: str = "") -> None:
        self.ai_motor = ai_motor
        self.gemini_api_key = gemini_api_key
        self.gemini_model = "gemini-3.5-flash"
        self.ollama_adresi = "http://localhost:11434"
        self.yerel_model = "test-model"


class SahteUretici:
    def __init__(self, etiket: str, patlar: bool = False) -> None:
        self.etiket = etiket
        self._patlar = patlar

    async def uret(self, ozet_veri: list[dict]) -> list[Any]:
        if self._patlar:
            raise RuntimeError(f"{self.etiket} patladı")
        return [{"kaynak": self.etiket}]


async def test_local_secilince_yerel_birincil_gemini_yedek_yok(monkeypatch):
    monkeypatch.setattr(
        "app.adapters.cikan._uretici_fabrika._yerel_oneri",
        lambda a: SahteUretici("yerel"),
    )
    # Gemini yardımcısı çağrılırsa test patlardı (anahtarsız Client) — çağrılmamalı.
    uretici = oneri_ureticisi_sec(SahteAyarlar(ai_motor="local"))

    assert isinstance(uretici, FallbackUretici)
    sonuc = await uretici.uret([{"x": 1}])
    assert sonuc == [{"kaynak": "yerel"}]  # birincil yerel


def test_gemini_secilince_anahtarla_gemini_doner(monkeypatch):
    monkeypatch.setattr(
        "app.adapters.cikan._uretici_fabrika._gemini_oneri",
        lambda a: SahteUretici("gemini"),
    )
    monkeypatch.setattr(
        "app.adapters.cikan._uretici_fabrika._yerel_oneri",
        lambda a: SahteUretici("yerel"),
    )
    uretici = oneri_ureticisi_sec(SahteAyarlar(ai_motor="gemini", gemini_api_key="k"))

    assert isinstance(uretici, FallbackUretici)


def test_gemini_secilip_anahtar_yoksa_ayar_hatasi():
    with pytest.raises(AyarHatasi) as hata:
        oneri_ureticisi_sec(SahteAyarlar(ai_motor="gemini", gemini_api_key=""))

    assert "GEMINI_API_KEY" in str(hata.value)


def test_bilinmeyen_motor_ayar_hatasi():
    with pytest.raises(AyarHatasi):
        oneri_ureticisi_sec(SahteAyarlar(ai_motor="baska"))


async def test_gemini_dususte_locale_fallback():
    fallback = FallbackUretici(
        birincil=SahteUretici("gemini", patlar=True),
        yedek=SahteUretici("yerel"),
    )

    sonuc = await fallback.uret([{"x": 1}])

    assert sonuc == [{"kaynak": "yerel"}]


async def test_local_dususte_yedek_yoksa_bos_doner():
    # yedek=None → local seçiliyken hata olsa bile Gemini'ye gitmez (hiç kurulmadı).
    fallback = FallbackUretici(
        birincil=SahteUretici("yerel", patlar=True),
        yedek=None,
    )

    sonuc = await fallback.uret([{"x": 1}])

    assert sonuc == []  # boş döner, Gemini'ye GİTMEZ (veri sızmaz)
