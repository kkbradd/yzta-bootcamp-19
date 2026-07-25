"""Simülatörün cihaz seçimi: --atla ile gerçek edge servisine yer açılır."""

import sys
from pathlib import Path

import pytest

# Simülatör uygulama paketinin dışında (compose'a volume ile bağlanan betik).
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "simulator"))

from simulator import yayinlanacak_cihazlar  # noqa: E402


def test_atlanacak_yoksa_tum_cihazlar_yayinlar():
    assert yayinlanacak_cihazlar(3, set()) == [1, 2, 3]


def test_atlanan_cihaz_listeden_cikarilir():
    assert yayinlanacak_cihazlar(6, {1}) == [2, 3, 4, 5, 6]


def test_birden_fazla_cihaz_atlanabilir():
    assert yayinlanacak_cihazlar(5, {2, 4}) == [1, 3, 5]


def test_aralik_disi_atlama_yok_sayilir():
    """--atla 99 gibi geçersiz numara sessizce etkisiz kalır, hata vermez."""
    assert yayinlanacak_cihazlar(3, {99}) == [1, 2, 3]


def test_tum_cihazlar_atlanirsa_liste_bos_doner():
    """Boş liste çağıranın hata basmasını sağlar (sessiz no-op olmamalı)."""
    assert yayinlanacak_cihazlar(2, {1, 2}) == []


@pytest.mark.parametrize("cihaz_sayisi", [0, -1])
def test_pozitif_olmayan_cihaz_sayisi_bos_doner(cihaz_sayisi):
    assert yayinlanacak_cihazlar(cihaz_sayisi, set()) == []
