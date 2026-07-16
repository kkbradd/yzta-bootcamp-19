"""model_hazirla birim testleri — Ollama'ya MockTransport ile, ağ yok."""

import json

import httpx

from app.model_hazirla import model_hazirla

MODEL = "qwen3.5:0.8b"


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
