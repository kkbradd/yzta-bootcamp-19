"""HTTP servisi birim testleri — TestClient + sahte asistan, model/ağ yok."""

from fastapi.testclient import TestClient

from app.cekirdek import AsistanCevabi
from app.servis import uygulama_olustur


class SahteAsistan:
    def __init__(self) -> None:
        self.sorulan: list[str] = []

    def sor(self, mesaj: str) -> AsistanCevabi:
        self.sorulan.append(mesaj)
        return AsistanCevabi(
            cevap="34 hattı şu an orta yoğunlukta.",
            tur_sayisi=2,
            arac_cagrilari=["hat_yogunluklari"],
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
