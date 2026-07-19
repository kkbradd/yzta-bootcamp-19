"""Ağırlık yükleme: yanlış dosya sessizce çöp üretmek yerine hata vermeli."""

import pytest

torch = pytest.importorskip("torch", reason="csrnet extra'sı kurulu değil")

from app.csrnet_agi import AgirlikHatasi, Csrnet, agi_yukle  # noqa: E402


def test_ag_beklenen_anahtarlari_tasir():
    anahtarlar = Csrnet().state_dict().keys()

    # leeyeehoo/CSRNet-pytorch checkpoint'iyle birebir eşleşmeli.
    assert "frontend.0.weight" in anahtarlar
    assert "backend.0.weight" in anahtarlar
    assert "output_layer.weight" in anahtarlar
    assert len(anahtarlar) == 34


def test_parametre_sayisi_referansla_ayni():
    assert sum(p.numel() for p in Csrnet().parameters()) == 16_263_489


def test_sarili_checkpoint_yuklenir(tmp_path):
    """Eğitim checkpoint'i state_dict/epoch/optimizer ile sarılı gelir."""
    yol = tmp_path / "sarili.pth.tar"
    torch.save({"epoch": 195, "state_dict": Csrnet().state_dict()}, yol)

    assert agi_yukle(yol) is not None


def test_ciplak_checkpoint_yuklenir(tmp_path):
    """HuggingFace kopyaları çıplak OrderedDict'tir."""
    yol = tmp_path / "ciplak.pth"
    torch.save(Csrnet().state_dict(), yol)

    assert agi_yukle(yol) is not None


def test_dataparallel_oneki_soyulur(tmp_path):
    yol = tmp_path / "onekli.pth"
    onekli = {f"module.{ad}": deger for ad, deger in Csrnet().state_dict().items()}
    torch.save(onekli, yol)

    assert agi_yukle(yol) is not None


def test_eksik_dosya_anlasilir_hata_verir(tmp_path):
    with pytest.raises(AgirlikHatasi, match="bulunamadı"):
        agi_yukle(tmp_path / "yok.pth.tar")


def test_uyusmayan_agirlik_reddedilir(tmp_path):
    """Farklı bir ağın ağırlığı sessizce yüklenip çöp sayım üretmemeli."""
    yol = tmp_path / "baska.pth"
    torch.save({"conv1.weight": torch.zeros(3, 3)}, yol)

    with pytest.raises(AgirlikHatasi, match="uyuşmuyor"):
        agi_yukle(yol)


def test_bozuk_dosya_reddedilir(tmp_path):
    """İndirme sırasında HTML hata sayfası kaydedilmiş olabilir."""
    yol = tmp_path / "bozuk.pth.tar"
    yol.write_text("<html>Google Drive virus scan warning</html>")

    with pytest.raises(AgirlikHatasi, match="okunamadı"):
        agi_yukle(yol)
