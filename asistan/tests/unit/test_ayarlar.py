"""Ayarlar birim testleri — ortam değişkeni okuma ve varsayılanlar."""

import dataclasses

import pytest

from app.ayarlar import Ayarlar

VARSAYILAN_YOTAY_API = "http://localhost:8000"
VARSAYILAN_OLLAMA = "http://localhost:11434"
VARSAYILAN_MODEL = "qwen3.5:0.8b"
VARSAYILAN_MOTOR = "ollama"


def _ortami_temizle(monkeypatch) -> None:
    for anahtar in ("YOTAY_API_ADRESI", "OLLAMA_ADRESI", "ASISTAN_MODEL", "ASISTAN_MOTOR"):
        monkeypatch.delenv(anahtar, raising=False)


def test_env_yokken_varsayilanlar_gecerli(monkeypatch):
    _ortami_temizle(monkeypatch)

    ayarlar = Ayarlar.ortamdan()

    assert ayarlar.yotay_api_adresi == VARSAYILAN_YOTAY_API
    assert ayarlar.ollama_adresi == VARSAYILAN_OLLAMA
    assert ayarlar.model == VARSAYILAN_MODEL
    assert ayarlar.motor == VARSAYILAN_MOTOR


def test_env_degiskenleri_varsayilanlari_ezer(monkeypatch):
    monkeypatch.setenv("YOTAY_API_ADRESI", "http://backend:8000")
    monkeypatch.setenv("OLLAMA_ADRESI", "http://ollama:11434")
    monkeypatch.setenv("ASISTAN_MODEL", "qwen3.5:9b")
    monkeypatch.setenv("ASISTAN_MOTOR", "llamacpp")

    ayarlar = Ayarlar.ortamdan()

    assert ayarlar.yotay_api_adresi == "http://backend:8000"
    assert ayarlar.ollama_adresi == "http://ollama:11434"
    assert ayarlar.model == "qwen3.5:9b"
    assert ayarlar.motor == "llamacpp"


def test_ayarlar_dondurulmus(monkeypatch):
    _ortami_temizle(monkeypatch)
    ayarlar = Ayarlar.ortamdan()

    with pytest.raises(dataclasses.FrozenInstanceError):
        ayarlar.model = "baska"  # type: ignore[misc]
