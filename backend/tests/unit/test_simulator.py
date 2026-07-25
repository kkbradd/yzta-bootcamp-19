"""Simülatörün cihaz seçimi: --atla ile gerçek edge servisine yer açılır."""

import sys
from pathlib import Path

import pytest

# Simülatör uygulama paketinin dışında (compose'a volume ile bağlanan betik).
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "simulator"))

from simulator import CihazDurumu, yayinlanacak_cihazlar  # noqa: E402


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


# ---- Yeniden bağlanma dayanıklılığı ----
#
# Yük altında kaçırılan tek bir MQTT keepalive broker'ın istemciyi düşürmesine
# yol açıyor ("exceeded timeout"); eskiden bu simülatör sürecini öldürüyordu.


def test_sira_no_zaman_tohumundan_baslar():
    """MQTT simülatörü ile geçmiş veri yükleyicisi aynı sayaç aralığını kullanmamalı."""
    durum = CihazDurumu(cihaz_no=1, tunel_sn=0)

    assert durum.sira_no > 1_700_000_000  # int(time.time()) tohumu


def test_sira_no_yeniden_baglanmada_geri_sarmaz():
    """Sayaç sıfırlansaydı ölçümler UNIQUE(cihaz_id, sira_no) ile sessizce yutulurdu."""
    durum = CihazDurumu(cihaz_no=1, tunel_sn=0)

    ilk = durum.sonraki_olcum()["sira_no"]
    ikinci = durum.sonraki_olcum()["sira_no"]

    assert ikinci == ilk + 1


def test_cihaz_kimligi_ve_topikleri():
    durum = CihazDurumu(cihaz_no=7, tunel_sn=0)

    assert durum.cihaz_id == "edge_0007"
    assert durum.yogunluk_topic == "filo/edge_0007/yogunluk"
    assert durum.durum_topic == "filo/edge_0007/durum"


def test_tunelsiz_cihaz_hemen_yayinlar():
    assert CihazDurumu(cihaz_no=1, tunel_sn=0).tunelde_mi is False


def test_tunel_suresince_biriktirilir():
    durum = CihazDurumu(cihaz_no=1, tunel_sn=60)

    assert durum.tunelde_mi is True


def test_olcum_gerekli_alanlari_tasir():
    olcum = CihazDurumu(cihaz_no=1, tunel_sn=0).sonraki_olcum()

    assert set(olcum) == {"sira_no", "kisi_sayisi", "timestamp"}
    assert olcum["kisi_sayisi"] >= 0
    assert olcum["timestamp"].endswith("Z")
