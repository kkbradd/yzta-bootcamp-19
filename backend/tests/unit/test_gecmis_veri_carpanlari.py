"""Geçmiş veri üreticisinin saatlik yoğunluk eğrisi (İBB akbil verisinden)."""

from datetime import UTC, datetime

import pytest

from app.gecmis_veri_yukle import (
    HAFTA_ICI_CARPANLARI,
    HAFTA_SONU_CARPANLARI,
    _kisi_sayisi_uret,
    _saat_carpani,
)

SAAT_DESENI = {"tip": "saat", "baslangic": 6, "bitis": 9}

# 2026-07-22 Çarşamba, 2026-07-26 Pazar
CARSAMBA = datetime(2026, 7, 22, tzinfo=UTC)
PAZAR = datetime(2026, 7, 26, tzinfo=UTC)


def test_carpan_tablolari_24_saat():
    assert len(HAFTA_ICI_CARPANLARI) == 24
    assert len(HAFTA_SONU_CARPANLARI) == 24


def test_hafta_ici_sabah_zirvesi_en_yuksek():
    """07:00 İBB verisinde günün en yoğun saati."""
    assert HAFTA_ICI_CARPANLARI[7] == max(HAFTA_ICI_CARPANLARI)


def test_hafta_sonu_sabah_zirvesi_yok():
    """Pazar sabahı zirve kaybolur — hafta sonu 'ölçeklenmiş iş günü' değildir."""
    assert HAFTA_SONU_CARPANLARI[7] < 0.25
    assert HAFTA_ICI_CARPANLARI[7] > 1.0


def test_hafta_sonu_zirvesi_ogleden_sonra():
    en_yogun_saat = HAFTA_SONU_CARPANLARI.index(max(HAFTA_SONU_CARPANLARI))
    assert 15 <= en_yogun_saat <= 19


def test_gece_saatleri_bos_degil():
    """Üsküdar'da gece hattı var; taban sıfır olmamalı."""
    assert all(carpan > 0 for carpan in HAFTA_ICI_CARPANLARI)
    assert min(HAFTA_ICI_CARPANLARI) < 0.1


def test_ogle_saatlerinde_belirgin_dusus_yok():
    """İBB verisinde öğle, zirvenin ~%50'sinin altına inmiyor."""
    ogle_ortalamasi = sum(HAFTA_ICI_CARPANLARI[11:15]) / 4
    assert ogle_ortalamasi > 0.5 * max(HAFTA_ICI_CARPANLARI)


def test_saat_carpani_hafta_ici_ve_sonu_ayirir():
    assert _saat_carpani(CARSAMBA.replace(hour=7)) == HAFTA_ICI_CARPANLARI[7]
    assert _saat_carpani(PAZAR.replace(hour=7)) == HAFTA_SONU_CARPANLARI[7]


@pytest.mark.parametrize("saat", range(24))
def test_uretilen_sayi_makul_aralikta(saat):
    kisi = _kisi_sayisi_uret(CARSAMBA.replace(hour=saat), SAAT_DESENI)
    assert 0 <= kisi <= 90


def test_zirve_saati_geceden_belirgin_yogun():
    """Rastgelelik zirve/gece ayrımını yutmamalı."""
    zirve = [_kisi_sayisi_uret(CARSAMBA.replace(hour=8), SAAT_DESENI) for _ in range(40)]
    gece = [_kisi_sayisi_uret(CARSAMBA.replace(hour=3), SAAT_DESENI) for _ in range(40)]
    assert min(zirve) > max(gece)


def test_hafta_sonu_sabahi_hafta_icinden_seyrek():
    hafta_ici = [_kisi_sayisi_uret(CARSAMBA.replace(hour=8), SAAT_DESENI) for _ in range(40)]
    hafta_sonu = [_kisi_sayisi_uret(PAZAR.replace(hour=8), SAAT_DESENI) for _ in range(40)]
    assert min(hafta_ici) > max(hafta_sonu)
