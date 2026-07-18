"""YOTAY tool birim testleri — httpx.MockTransport ile, ağ erişimi yok."""

from datetime import datetime
from typing import Any

import httpx

from app.araclar import (
    HatAnlikDurumAraci,
    HatTrendAraci,
    HatYogunluklariAraci,
    YotayVeriKaynagi,
)

HATLAR_YANITI = [
    {
        "hat_id": 1,
        "hat_no": "34",
        "ad": "Zincirlikuyu – Söğütlüçeşme",
        "ortalama_doluluk": 0.62,
        "seviye": "orta",
        "arac_sayisi": 2,
    },
    {
        "hat_id": 2,
        "hat_no": "19T",
        "ad": "Taksim – Tuzla",
        "ortalama_doluluk": None,
        "seviye": None,
        "arac_sayisi": 0,
    },
]

ANLIK_YANITI = [
    {
        "arac_id": 3,
        "kisi_sayisi": 45,
        "doluluk_orani": 0.75,
        "seviye": "yogun",
        "zaman": "2026-07-16T14:22:00+00:00",
    },
]

TREND_YANITI = [
    {
        "zaman": "2026-07-16T13:00:00+00:00",
        "ortalama_doluluk": 0.5,
        "ortalama_kisi": 30.0,
        "olcum_sayisi": 12,
    },
]


def _sahte_kaynak(
    yanitlar: dict[str, Any],
    istekler: list[httpx.Request] | None = None,
) -> YotayVeriKaynagi:
    def isleyici(istek: httpx.Request) -> httpx.Response:
        if istekler is not None:
            istekler.append(istek)
        govde = yanitlar.get(istek.url.path)
        if govde is None:
            return httpx.Response(404, json={"detail": "bulunamadı"})
        return httpx.Response(200, json=govde)

    istemci = httpx.Client(transport=httpx.MockTransport(isleyici), base_url="http://test")
    return YotayVeriKaynagi(istemci)


def _kopuk_kaynak() -> YotayVeriKaynagi:
    def isleyici(istek: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("bağlantı reddedildi")

    istemci = httpx.Client(transport=httpx.MockTransport(isleyici), base_url="http://test")
    return YotayVeriKaynagi(istemci)


# ---- hat_yogunluklari ----


def test_hat_yogunluklari_ozet_metni_uretir():
    arac = HatYogunluklariAraci(_sahte_kaynak({"/api/hatlar": HATLAR_YANITI}))

    sonuc = arac.execute()

    assert sonuc.success
    assert "34" in sonuc.content
    assert "%62" in sonuc.content
    assert "orta" in sonuc.content


def test_hat_yogunluklari_olcum_yoksa_veri_yok_der():
    arac = HatYogunluklariAraci(_sahte_kaynak({"/api/hatlar": HATLAR_YANITI}))

    sonuc = arac.execute()

    assert "19T" in sonuc.content
    assert "veri yok" in sonuc.content


# ---- hat_anlik_durum ----


def test_hat_anlik_durum_hat_no_ile_bulur():
    kaynak = _sahte_kaynak({"/api/hatlar": HATLAR_YANITI, "/api/hatlar/1/anlik": ANLIK_YANITI})
    arac = HatAnlikDurumAraci(kaynak)

    sonuc = arac.execute(hat_no="34")

    assert sonuc.success
    assert "45" in sonuc.content
    assert "%75" in sonuc.content
    assert "yogun" in sonuc.content


def test_hat_anlik_durum_bilinmeyen_hatta_mevcutlari_sayar():
    arac = HatAnlikDurumAraci(_sahte_kaynak({"/api/hatlar": HATLAR_YANITI}))

    sonuc = arac.execute(hat_no="99")

    assert sonuc.success
    assert "bulunamadı" in sonuc.content
    assert "34" in sonuc.content


# ---- hat_trend ----


def test_hat_trend_zaman_araligini_saat_sayisindan_kurar():
    istekler: list[httpx.Request] = []
    kaynak = _sahte_kaynak(
        {"/api/hatlar": HATLAR_YANITI, "/api/hatlar/1/trend": TREND_YANITI},
        istekler,
    )
    arac = HatTrendAraci(kaynak)

    sonuc = arac.execute(hat_no="34", saat_sayisi=3)

    assert sonuc.success
    trend_istegi = next(i for i in istekler if i.url.path.endswith("/trend"))
    baslangic = datetime.fromisoformat(trend_istegi.url.params["baslangic"])
    bitis = datetime.fromisoformat(trend_istegi.url.params["bitis"])
    assert (bitis - baslangic).total_seconds() == 3 * 3600
    assert trend_istegi.url.params["aralik"] == "saat"


def test_hat_trend_nokta_verilerini_metne_cevirir():
    kaynak = _sahte_kaynak({"/api/hatlar": HATLAR_YANITI, "/api/hatlar/1/trend": TREND_YANITI})
    arac = HatTrendAraci(kaynak)

    sonuc = arac.execute(hat_no="34")

    assert "%50" in sonuc.content
    assert "13:00" in sonuc.content


def test_hat_trend_gecersiz_saat_sayisina_aciklayici_mesaj_doner():
    kaynak = _sahte_kaynak({"/api/hatlar": HATLAR_YANITI, "/api/hatlar/1/trend": TREND_YANITI})
    arac = HatTrendAraci(kaynak)

    sonuc = arac.execute(hat_no="34", saat_sayisi="üç")

    assert sonuc.success
    assert "saat_sayisi" in sonuc.content


def test_hat_trend_kayit_yoksa_bilgi_verir():
    kaynak = _sahte_kaynak({"/api/hatlar": HATLAR_YANITI, "/api/hatlar/1/trend": []})
    arac = HatTrendAraci(kaynak)

    sonuc = arac.execute(hat_no="34", saat_sayisi=1)

    assert sonuc.success
    assert "kayıt yok" in sonuc.content


# ---- ortak davranışlar ----


def test_api_ulasilamazsa_basarisiz_sonuc_doner():
    arac = HatYogunluklariAraci(_kopuk_kaynak())

    sonuc = arac.execute()

    assert not sonuc.success
    assert "YOTAY API" in sonuc.content


def test_spec_adlari_ve_zorunlu_parametreler():
    kaynak = _sahte_kaynak({})

    yogunluk = HatYogunluklariAraci(kaynak).spec
    anlik = HatAnlikDurumAraci(kaynak).spec
    trend = HatTrendAraci(kaynak).spec

    assert yogunluk.name == "hat_yogunluklari"
    assert yogunluk.parameters["required"] == []
    assert anlik.name == "hat_anlik_durum"
    assert anlik.parameters["required"] == ["hat_no"]
    assert trend.name == "hat_trend"
    assert trend.parameters["required"] == ["hat_no"]
