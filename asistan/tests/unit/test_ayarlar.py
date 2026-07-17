"""Ayarlar birim testleri — ortam değişkeni okuma ve varsayılanlar."""

import dataclasses

import pytest

from app.ayarlar import AyarHatasi, Ayarlar

VARSAYILAN_YOTAY_API = "http://localhost:8000"
VARSAYILAN_OLLAMA = "http://localhost:11434"
VARSAYILAN_MODEL = "qwen3.5:0.8b"
VARSAYILAN_MOTOR = "ollama"
BULUT_MOTORU = "cloud"
GEMINI_MODELI = "gemini-3-flash"


def _ortami_temizle(monkeypatch) -> None:
    for anahtar in (
        "YOTAY_API_ADRESI",
        "OLLAMA_ADRESI",
        "ASISTAN_MODEL",
        "ASISTAN_MOTOR",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
    ):
        monkeypatch.delenv(anahtar, raising=False)


def _gemini_ortami(monkeypatch, anahtar: str | None) -> None:
    _ortami_temizle(monkeypatch)
    monkeypatch.setenv("ASISTAN_MOTOR", BULUT_MOTORU)
    monkeypatch.setenv("ASISTAN_MODEL", GEMINI_MODELI)
    if anahtar is not None:
        monkeypatch.setenv("GEMINI_API_KEY", anahtar)


def test_env_yokken_varsayilanlar_gecerli(monkeypatch):
    _ortami_temizle(monkeypatch)

    ayarlar = Ayarlar.ortamdan()

    assert ayarlar.yotay_api_adresi == VARSAYILAN_YOTAY_API
    assert ayarlar.ollama_adresi == VARSAYILAN_OLLAMA
    assert ayarlar.model == VARSAYILAN_MODEL
    assert ayarlar.motor == VARSAYILAN_MOTOR
    assert ayarlar.gemini_anahtari == ""


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


# ---- Gemini (opsiyonel bulut motoru) ----


def test_gemini_anahtari_env_den_okunur(monkeypatch):
    _gemini_ortami(monkeypatch, "gizli-anahtar")

    ayarlar = Ayarlar.ortamdan()

    assert ayarlar.gemini_anahtari == "gizli-anahtar"


def test_google_api_key_de_kabul_edilir(monkeypatch):
    _gemini_ortami(monkeypatch, anahtar=None)
    monkeypatch.setenv("GOOGLE_API_KEY", "google-anahtari")

    ayarlar = Ayarlar.ortamdan()

    assert ayarlar.gemini_anahtari == "google-anahtari"


def test_gemini_api_key_google_api_key_i_ezer(monkeypatch):
    _gemini_ortami(monkeypatch, "gemini-anahtari")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-anahtari")

    ayarlar = Ayarlar.ortamdan()

    assert ayarlar.gemini_anahtari == "gemini-anahtari"


def test_gemini_modelinde_anahtar_yoksa_reddedilir(monkeypatch):
    _gemini_ortami(monkeypatch, anahtar=None)

    with pytest.raises(AyarHatasi) as hata:
        Ayarlar.ortamdan()

    assert "GEMINI_API_KEY" in str(hata.value)


def test_gemini_modelinde_anahtar_varsa_kabul_edilir(monkeypatch):
    _gemini_ortami(monkeypatch, "gizli-anahtar")

    ayarlar = Ayarlar.ortamdan()

    assert ayarlar.gemini_mi


def test_lokal_motor_anahtarsiz_calisir(monkeypatch):
    _ortami_temizle(monkeypatch)

    ayarlar = Ayarlar.ortamdan()

    assert not ayarlar.gemini_mi


def test_gemini_mi_model_adina_bakar(monkeypatch):
    _ortami_temizle(monkeypatch)
    monkeypatch.setenv("ASISTAN_MOTOR", BULUT_MOTORU)
    monkeypatch.setenv("ASISTAN_MODEL", "gpt-4o")
    monkeypatch.setenv("GEMINI_API_KEY", "gizli-anahtar")

    ayarlar = Ayarlar.ortamdan()

    assert not ayarlar.gemini_mi
