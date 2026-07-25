"""HTTP servisi birim testleri — TestClient + sahte asistan, model/ağ yok."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.ayarlar import SECILEBILIR_MODEL_ADLARI, AyarHatasi
from app.cekirdek import AsistanCevabi
from app.servis import uygulama_olustur

PANEL_ORIGINI = "http://localhost:3000"


class SahteAsistan:
    def __init__(self) -> None:
        self.sorulan: list[str] = []
        self.istenen_modeller: list[str | None] = []

    def sor(self, mesaj: str, model: str | None = None) -> AsistanCevabi:
        self.sorulan.append(mesaj)
        self.istenen_modeller.append(model)
        return AsistanCevabi(
            cevap="34 hattı şu an orta yoğunlukta.",
            tur_sayisi=2,
            arac_cagrilari=["hat_yogunluklari"],
            model=model or "qwen3.5:0.8b",
        )


def _istemci(asistan: SahteAsistan | None = None) -> TestClient:
    sahte = asistan or SahteAsistan()
    return TestClient(uygulama_olustur(asistan_fabrikasi=lambda: sahte))


def test_chat_cevap_ve_arac_cagrilarini_doner():
    sahte = SahteAsistan()

    with _istemci(sahte) as istemci:
        yanit = istemci.post("/chat", json={"mesaj": "34 hattı nasıl?"})

    assert yanit.status_code == 200
    govde = yanit.json()
    assert govde["cevap"] == "34 hattı şu an orta yoğunlukta."
    assert govde["tur_sayisi"] == 2
    assert govde["arac_cagrilari"] == ["hat_yogunluklari"]
    assert sahte.sorulan == ["34 hattı nasıl?"]


def test_bos_mesaj_reddedilir():
    with _istemci() as istemci:
        yanit = istemci.post("/chat", json={"mesaj": ""})

    assert yanit.status_code == 422


def test_mesaj_alani_zorunlu():
    with _istemci() as istemci:
        yanit = istemci.post("/chat", json={})

    assert yanit.status_code == 422


def test_saglik_ucu_calisiyor_der():
    with _istemci() as istemci:
        yanit = istemci.get("/saglik")

    assert yanit.status_code == 200
    assert yanit.json() == {"durum": "calisiyor"}


# ---- CORS: panel farklı origin'den (port 3000) çağırır ----


def test_panel_origininden_on_kontrol_kabul_edilir():
    with _istemci() as istemci:
        yanit = istemci.options(
            "/chat",
            headers={
                "Origin": PANEL_ORIGINI,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

    assert yanit.status_code == 200
    assert yanit.headers["access-control-allow-origin"] == PANEL_ORIGINI


def test_panel_origininden_chat_yanitinda_cors_basligi_doner():
    with _istemci() as istemci:
        yanit = istemci.post("/chat", json={"mesaj": "selam"}, headers={"Origin": PANEL_ORIGINI})

    assert yanit.status_code == 200
    assert yanit.headers["access-control-allow-origin"] == PANEL_ORIGINI


def test_izinsiz_originden_cors_basligi_donmez():
    with _istemci() as istemci:
        yanit = istemci.post(
            "/chat", json={"mesaj": "selam"}, headers={"Origin": "http://kotu-site.example"}
        )

    assert "access-control-allow-origin" not in yanit.headers


def test_joker_origin_reddedilir(monkeypatch):
    monkeypatch.setenv("ASISTAN_CORS_IZINLI_ORIGINLER", "*")

    with pytest.raises(AyarHatasi) as hata:
        uygulama_olustur(asistan_fabrikasi=SahteAsistan)

    assert "*" in str(hata.value)


def test_secilen_model_asistana_iletilir():
    sahte = SahteAsistan()
    with _istemci(sahte) as istemci:
        yanit = istemci.post("/chat", json={"mesaj": "selam", "model": "qwen3.5:1.7b"})

    assert yanit.status_code == 200
    assert sahte.istenen_modeller == ["qwen3.5:1.7b"]
    assert yanit.json()["model"] == "qwen3.5:1.7b"


def test_model_verilmezse_varsayilan_kullanilir():
    sahte = SahteAsistan()
    with _istemci(sahte) as istemci:
        istemci.post("/chat", json={"mesaj": "selam"})

    assert sahte.istenen_modeller == [None]


def test_listede_olmayan_model_reddedilir():
    """Serbest model adı `/api/pull` ile keyfi indirme tetikleyebilirdi."""
    sahte = SahteAsistan()
    with _istemci(sahte) as istemci:
        yanit = istemci.post("/chat", json={"mesaj": "selam", "model": "llama3:70b"})

    assert yanit.status_code == 400
    assert sahte.sorulan == []


def test_modeller_listesi_secilebilirleri_doner(monkeypatch):
    # Geliştirici makinesinde Ollama ayakta olabilir; test ağdan bağımsız kalmalı.
    monkeypatch.setattr("app.servis.mevcut_modeller", lambda istemci: ["qwen3.5:1.7b"])

    with _istemci() as istemci:
        yanit = istemci.get("/modeller")

    assert yanit.status_code == 200
    modeller = yanit.json()
    assert [m["ad"] for m in modeller] == list(SECILEBILIR_MODEL_ADLARI)
    indirilme = {m["ad"]: m["indirildi_mi"] for m in modeller}
    assert indirilme["qwen3.5:1.7b"] is True
    assert indirilme["qwen3.5:4b"] is False
    assert sum(m["varsayilan_mi"] for m in modeller) == 1


def test_ollamaya_ulasilamazsa_liste_yine_doner(monkeypatch):
    """Boş sayfa yerine 'indirilmedi' durumu gösterilmeli."""

    def patla(istemci):
        raise httpx.ConnectError("bağlanılamadı")

    monkeypatch.setattr("app.servis.mevcut_modeller", patla)

    with _istemci() as istemci:
        yanit = istemci.get("/modeller")

    assert yanit.status_code == 200
    assert all(m["indirildi_mi"] is False for m in yanit.json())


def test_listede_olmayan_model_indirilemez():
    with _istemci() as istemci:
        yanit = istemci.post("/modeller/indir", json={"model": "llama3:70b"})

    assert yanit.status_code == 400
