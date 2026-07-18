"""model_hazirla birim testleri — Ollama'ya MockTransport ile, ağ yok."""

import json

import httpx

from app.ayarlar import Ayarlar
from app.model_hazirla import hazirlik_yap, model_hazirla

MODEL = "qwen3.5:0.8b"
LOKAL_AYARLAR = Ayarlar(
    yotay_api_adresi="http://test",
    ollama_adresi="http://test:11434",
    model=MODEL,
    motor="ollama",
)
GEMINI_AYARLARI = Ayarlar(
    yotay_api_adresi="http://test",
    ollama_adresi="http://test:11434",
    model="gemini-3-flash",
    motor="cloud",
    gemini_anahtari="gizli-anahtar",
)


def _istemci(mevcut_modeller: list[str], cekilenler: list[str]) -> httpx.Client:
    def isleyici(istek: httpx.Request) -> httpx.Response:
        if istek.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": m} for m in mevcut_modeller]})
        if istek.url.path == "/api/pull":
            cekilenler.append(json.loads(istek.content)["name"])
            return httpx.Response(200, json={"status": "success"})
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(isleyici), base_url="http://test")


def test_model_zaten_varsa_cekmez():
    cekilenler: list[str] = []

    model_hazirla(MODEL, istemci=_istemci([MODEL, "baska:1b"], cekilenler))

    assert cekilenler == []


def test_model_yoksa_ceker():
    cekilenler: list[str] = []

    model_hazirla(MODEL, istemci=_istemci(["baska:1b"], cekilenler))

    assert cekilenler == [MODEL]


# ---- hazirlik_yap: Gemini modunda Ollama'ya hiç dokunulmaz ----


def _sayan_istemci(istekler: list[str]) -> httpx.Client:
    def isleyici(istek: httpx.Request) -> httpx.Response:
        istekler.append(istek.url.path)
        return httpx.Response(200, json={"models": []})

    return httpx.Client(transport=httpx.MockTransport(isleyici), base_url="http://test")


def test_gemini_modunda_ollamaya_istek_atilmaz():
    istekler: list[str] = []

    hazirlik_yap(GEMINI_AYARLARI, istemci_kur=lambda: _sayan_istemci(istekler))

    assert istekler == []


def test_lokal_modda_model_cekilir():
    cekilenler: list[str] = []

    hazirlik_yap(LOKAL_AYARLAR, istemci_kur=lambda: _istemci(["baska:1b"], cekilenler))

    assert cekilenler == [MODEL]
