"""domain/seviye.py saf fonksiyonlarının birim testleri (plan Bölüm 8.2).

Eşik sözleşmesi: oran < seyrek_ust → seyrek; seyrek_ust–orta_ust → orta; üstü → yogun.
"""

import pytest

from app.domain.seviye import (
    SEVIYE_ORTA,
    SEVIYE_SEYREK,
    SEVIYE_YOGUN,
    doluluk_orani_hesapla,
    seviye_belirle,
)

SEYREK_UST = 0.40
ORTA_UST = 0.70


def test_oran_kisi_bolu_kapasitedir() -> None:
    assert doluluk_orani_hesapla(kisi_sayisi=45, kapasite=90) == pytest.approx(0.5)


def test_asiri_doluluk_1e_kirpilmaz() -> None:
    # Plan 8.2: 1.0'a KIRPMA — aşırı doluluk görünür kalsın.
    assert doluluk_orani_hesapla(kisi_sayisi=36, kapasite=30) == pytest.approx(1.2)


@pytest.mark.parametrize(
    ("oran", "beklenen"),
    [
        (0.0, SEVIYE_SEYREK),
        (0.39, SEVIYE_SEYREK),
        (0.40, SEVIYE_ORTA),  # alt sınır dahil
        (0.70, SEVIYE_ORTA),  # üst sınır dahil
        (0.71, SEVIYE_YOGUN),
        (1.2, SEVIYE_YOGUN),
    ],
)
def test_seviye_esikleri(oran: float, beklenen: str) -> None:
    assert seviye_belirle(oran, seyrek_ust=SEYREK_UST, orta_ust=ORTA_UST) == beklenen
