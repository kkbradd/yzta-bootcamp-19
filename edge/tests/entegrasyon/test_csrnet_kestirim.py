"""Gerçek ağırlıkla sayım doğruluğu — iki sessiz hatanın regresyon kilidi.

Yanlış normalizasyon şeması (deponun val.ipynb'sindeki) ölçüldüğünde gürültüden
55.9 kişi halüsinasyonu üretiyor; yanlış ağırlık (Part A) düz karede 7.33 hayalet
kişi veriyor. İkisi de kod çalışıyormuş gibi görünüp sayıyı bozar.

Çalıştırmak için model/README.md'deki ağırlık indirilmiş olmalı:
    uv run pytest -m entegrasyon
"""

from pathlib import Path

import pytest

pytest.importorskip("torch", reason="csrnet extra'sı kurulu değil")
pytest.importorskip("cv2", reason="csrnet extra'sı kurulu değil")

import numpy as np  # noqa: E402

from app.csrnet_kestirim import CsrnetKestirici  # noqa: E402

# tests/entegrasyon/x.py -> edge/ -> depo kökü; model/ kökte durur.
AGIRLIK_YOLU = Path(__file__).resolve().parents[3] / "model" / "csrnet_partB.pth"
# Part B düz karede 0.13 veriyor; Part A 7.33. Eşik ikisini ayırt eder.
BOS_SAHNE_UST_SINIRI = 2

pytestmark = pytest.mark.entegrasyon


@pytest.fixture(scope="module")
def kestirici():
    if not AGIRLIK_YOLU.is_file():
        pytest.skip(f"ağırlık yok: {AGIRLIK_YOLU} (bkz. model/README.md)")
    return CsrnetKestirici(agirlik_yolu=AGIRLIK_YOLU, is_parcacigi=4, sayim_carpani=1.0)


def _duz_kare(deger: int) -> np.ndarray:
    return np.full((360, 480, 3), deger, dtype=np.uint8)


def test_bos_sahnede_sayim_sifira_yakin(kestirici):
    """Part A yüklenmişse burası patlar (7.33), Part B geçer (0.13)."""
    assert kestirici.kestir(_duz_kare(128)) <= BOS_SAHNE_UST_SINIRI


def test_gurultuden_kalabalik_uretmez(kestirici):
    """Yanlış normalizasyon şemasında bu 55.9 döner."""
    rastgele = np.random.default_rng(seed=0)
    gurultu = rastgele.integers(0, 256, size=(360, 480, 3), dtype=np.uint8)

    assert kestirici.kestir(gurultu) < 20


def test_sayim_negatif_donmez(kestirici):
    """Son katman sınırsız; negatif değer backend'de sessizce düşürülürdü."""
    assert kestirici.kestir(_duz_kare(255)) >= 0


def test_carpan_sayimi_olcekler(kestirici):
    kare = _duz_kare(100)
    tek_kat = kestirici.kestir(kare)

    on_kat_kestirici = CsrnetKestirici(
        agirlik_yolu=AGIRLIK_YOLU, is_parcacigi=4, sayim_carpani=10.0
    )

    assert on_kat_kestirici.kestir(kare) >= tek_kat
