"""AI_MOTOR seçimine göre öneri/uyarı üreticisini kurar.

`local`: yerel (SimpleAgent+Ollama) birincil, Gemini'ye fallback YOK (gizlilik).
`gemini`: Gemini birincil, yerele fallback VAR (güvenli yön) — anahtar zorunlu.
Tutarsız/eksik yapılandırma açılışta AyarHatasi ile reddedilir (sessiz çökme yok).
"""

from typing import Any

from app.adapters.cikan._fallback import FallbackUretici

MOTOR_YEREL = "local"
MOTOR_GEMINI = "gemini"


class AyarHatasi(ValueError):
    """AI motoru yapılandırması tutarsız — servis açılmadan fark edilir."""


def _yerel_oneri(ayarlar: Any):
    from app.adapters.cikan.simple_oneri import SimpleOneriUreticisi

    return SimpleOneriUreticisi(motor=_ollama_motoru(ayarlar), model=ayarlar.yerel_model)


def _gemini_oneri(ayarlar: Any):
    from app.adapters.cikan.gemini_oneri import GeminiOneriUreticisi

    return GeminiOneriUreticisi(api_key=ayarlar.gemini_api_key, model=ayarlar.gemini_model)


def _yerel_uyari(ayarlar: Any):
    from app.adapters.cikan.simple_uyari import SimpleUyariUreticisi

    return SimpleUyariUreticisi(motor=_ollama_motoru(ayarlar), model=ayarlar.yerel_model)


def _gemini_uyari(ayarlar: Any):
    from app.adapters.cikan.gemini_uyari import GeminiUyariUreticisi

    return GeminiUyariUreticisi(api_key=ayarlar.gemini_api_key, model=ayarlar.gemini_model)


def _ollama_motoru(ayarlar: Any):
    from openjarvis.core.config import load_config
    from openjarvis.engine import get_engine

    config = load_config()
    config.analytics.enabled = False  # gizlilik: anonim telemetriyi kapat
    config.engine.ollama.host = ayarlar.ollama_adresi
    _, motor = get_engine(config, engine_key="ollama")
    return motor


def _dogrula(ayarlar: Any) -> None:
    if ayarlar.ai_motor not in (MOTOR_YEREL, MOTOR_GEMINI):
        raise AyarHatasi(
            f"AI_MOTOR '{ayarlar.ai_motor}' geçersiz; '{MOTOR_YEREL}' veya '{MOTOR_GEMINI}' olmalı."
        )
    if ayarlar.ai_motor == MOTOR_GEMINI and not ayarlar.gemini_api_key:
        raise AyarHatasi("AI_MOTOR=gemini için GEMINI_API_KEY gerekli; local için gerekmez.")


def oneri_ureticisi_sec(ayarlar: Any) -> FallbackUretici:
    _dogrula(ayarlar)
    if ayarlar.ai_motor == MOTOR_YEREL:
        # Gemini yedeği HİÇ kurulmaz: anahtarsız çökmez ve veri Google'a sızamaz.
        return FallbackUretici(_yerel_oneri(ayarlar), yedek=None)
    return FallbackUretici(_gemini_oneri(ayarlar), _yerel_oneri(ayarlar))


def uyari_ureticisi_sec(ayarlar: Any) -> FallbackUretici:
    _dogrula(ayarlar)
    if ayarlar.ai_motor == MOTOR_YEREL:
        return FallbackUretici(_yerel_uyari(ayarlar), yedek=None)
    return FallbackUretici(_gemini_uyari(ayarlar), _yerel_uyari(ayarlar))
