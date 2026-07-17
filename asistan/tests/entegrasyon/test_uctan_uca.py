"""Uçtan uca entegrasyon testi — gerçek backend + Ollama gerektirir.

Çalıştırma: backend compose ayakta ve seed+simülatör veri akıtmışken
    uv run pytest tests/entegrasyon -m entegrasyon
"""

import httpx
import pytest

from app.ayarlar import Ayarlar
from app.cekirdek import YotayAsistani

pytestmark = pytest.mark.entegrasyon

SAGLIK_ZAMAN_ASIMI_SN = 2.0


def _backend_ayakta(adres: str) -> bool:
    try:
        return httpx.get(f"{adres}/api/saglik", timeout=SAGLIK_ZAMAN_ASIMI_SN).status_code == 200
    except httpx.HTTPError:
        return False


@pytest.fixture(scope="module")
def asistan() -> YotayAsistani:
    ayarlar = Ayarlar.ortamdan()
    if not _backend_ayakta(ayarlar.yotay_api_adresi):
        pytest.skip("YOTAY backend ayakta değil")
    return YotayAsistani.ayarlardan(ayarlar)


def test_genel_yogunluk_sorusuna_gercek_veriyle_cevap_verir(asistan: YotayAsistani):
    cevap = asistan.sor("Şu an hatlarda yoğunluk nasıl?")

    assert cevap.arac_cagrilari, "asistan hiç tool çağırmadı"
    assert cevap.cevap.strip()


def test_belirli_hattin_anlik_durumunu_getirir(asistan: YotayAsistani):
    cevap = asistan.sor("34 hattında şu an kaç araç var, doluluk nasıl?")

    assert cevap.arac_cagrilari, "asistan hiç tool çağırmadı"
    assert "34" in cevap.cevap
