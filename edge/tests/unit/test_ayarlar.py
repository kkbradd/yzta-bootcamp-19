"""Ayar doğrulaması: tutarsız yapılandırma servis açılmadan yakalanmalı."""

import pytest

from app.ayarlar import CSRNET_MOTORU, SAHTE_MOTOR, Ayarlar, EdgeAyarHatasi


@pytest.fixture(autouse=True)
def _ortami_temizle(monkeypatch):
    for degisken in (
        "EDGE_MOTOR",
        "EDGE_VIDEO_YOLU",
        "EDGE_AGIRLIK_YOLU",
        "EDGE_YAYIN_PERIYODU_SN",
        "EDGE_PORT",
    ):
        monkeypatch.delenv(degisken, raising=False)


def test_varsayilan_sahte_motorla_calisir():
    ayarlar = Ayarlar.ortamdan()
    assert ayarlar.motor == SAHTE_MOTOR
    assert not ayarlar.csrnet_mi


def test_gecersiz_motor_reddedilir(monkeypatch):
    monkeypatch.setenv("EDGE_MOTOR", "yolo")
    with pytest.raises(EdgeAyarHatasi, match="EDGE_MOTOR"):
        Ayarlar.ortamdan()


def test_sifir_periyot_reddedilir(monkeypatch):
    monkeypatch.setenv("EDGE_YAYIN_PERIYODU_SN", "0")
    with pytest.raises(EdgeAyarHatasi, match="pozitif"):
        Ayarlar.ortamdan()


def test_sayisal_olmayan_periyot_reddedilir(monkeypatch):
    monkeypatch.setenv("EDGE_YAYIN_PERIYODU_SN", "iki")
    with pytest.raises(EdgeAyarHatasi, match="sayı olmalı"):
        Ayarlar.ortamdan()


def test_csrnet_videosuz_reddedilir(monkeypatch):
    monkeypatch.setenv("EDGE_MOTOR", CSRNET_MOTORU)
    with pytest.raises(EdgeAyarHatasi, match="EDGE_VIDEO_YOLU"):
        Ayarlar.ortamdan()


def test_csrnet_agirliksiz_reddedilir(monkeypatch, tmp_path):
    video = tmp_path / "otobus.mp4"
    video.write_bytes(b"sahte")
    monkeypatch.setenv("EDGE_MOTOR", CSRNET_MOTORU)
    monkeypatch.setenv("EDGE_VIDEO_YOLU", str(video))
    with pytest.raises(EdgeAyarHatasi, match="ağırlığı bulunamadı|EDGE_AGIRLIK_YOLU"):
        Ayarlar.ortamdan()


def test_csrnet_tam_yapilandirmayla_gecer(monkeypatch, tmp_path):
    video = tmp_path / "otobus.mp4"
    video.write_bytes(b"sahte")
    agirlik = tmp_path / "partBmodel_best.pth.tar"
    agirlik.write_bytes(b"sahte")
    monkeypatch.setenv("EDGE_MOTOR", CSRNET_MOTORU)
    monkeypatch.setenv("EDGE_VIDEO_YOLU", str(video))
    monkeypatch.setenv("EDGE_AGIRLIK_YOLU", str(agirlik))

    ayarlar = Ayarlar.ortamdan()

    assert ayarlar.csrnet_mi
    assert ayarlar.video_yolu == video


def test_sahte_motor_video_istemez(monkeypatch):
    """Boru hattı modelsiz test edilebilsin diye sahte mod dosya aramaz."""
    monkeypatch.setenv("EDGE_MOTOR", SAHTE_MOTOR)
    assert Ayarlar.ortamdan().motor == SAHTE_MOTOR
