"""YOTAY veri araçları — asistanın backend REST API'sinden okuduğu OpenJarvis tool'ları.

Tool çıktıları küçük modele uygun kısa Türkçe metindir; hata istisnaları yutulmaz,
API hataları `ToolResult(success=False)`, kullanıcı kaynaklı durumlar (bilinmeyen hat,
geçersiz parametre) açıklayıcı bilgi metni olarak döner.
"""

from abc import abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from openjarvis.core.types import ToolResult
from openjarvis.tools._stubs import BaseTool, ToolSpec

from app.ayarlar import ISTEK_ZAMAN_ASIMI_SN, VARSAYILAN_TREND_SAATI


class HatBulunamadi(Exception):
    """Sorulan hat sistemde yok; mesajı modele bilgi olarak döner."""


class YotayVeriKaynagi:
    """Backend REST API'sine ince istemci; test httpx.Client'ı doğrudan verir."""

    def __init__(self, istemci: httpx.Client) -> None:
        self._istemci = istemci

    @classmethod
    def adresten(cls, adres: str) -> "YotayVeriKaynagi":
        return cls(httpx.Client(base_url=adres, timeout=ISTEK_ZAMAN_ASIMI_SN))

    def getir(self, yol: str, params: dict[str, Any] | None = None) -> Any:
        yanit = self._istemci.get(yol, params=params)
        yanit.raise_for_status()
        return yanit.json()

    def hatlari_getir(self) -> list[dict[str, Any]]:
        return self.getir("/api/hatlar")


def _yuzde(oran: float | None) -> str:
    return "veri yok" if oran is None else f"%{round(oran * 100)}"


def _hat_satiri(hat: dict[str, Any]) -> str:
    kimlik = f"{hat['hat_no']} ({hat['ad']})"
    if hat["ortalama_doluluk"] is None:
        return f"{kimlik}: henüz veri yok"
    doluluk = _yuzde(hat["ortalama_doluluk"])
    return f"{kimlik}: doluluk {doluluk}, seviye {hat['seviye']}, {hat['arac_sayisi']} araç"


def _arac_satiri(arac: dict[str, Any]) -> str:
    doluluk = _yuzde(arac["doluluk_orani"])
    kisi = f"{arac['kisi_sayisi']} kişi"
    return f"Araç {arac['arac_id']}: {kisi}, doluluk {doluluk}, seviye {arac['seviye']}"


def _trend_satiri(nokta: dict[str, Any]) -> str:
    saat = datetime.fromisoformat(nokta["zaman"]).strftime("%H:%M")
    doluluk = _yuzde(nokta["ortalama_doluluk"])
    return f"{saat}: doluluk {doluluk}, ortalama {round(nokta['ortalama_kisi'])} kişi"


def _trend_parametreleri(saat_sayisi: int) -> dict[str, str]:
    bitis = datetime.now(UTC)
    baslangic = bitis - timedelta(hours=saat_sayisi)
    return {"baslangic": baslangic.isoformat(), "bitis": bitis.isoformat(), "aralik": "saat"}


class _YotayAraci(BaseTool):
    """Ortak şablon: hata ve 'hat yok' akışı tek yerde; alt sınıf yalnız `_calistir` yazar."""

    def __init__(self, kaynak: YotayVeriKaynagi) -> None:
        self._kaynak = kaynak

    def execute(self, **params: Any) -> ToolResult:
        try:
            return ToolResult(tool_name=self.spec.name, content=self._calistir(**params))
        except HatBulunamadi as bilgi:
            return ToolResult(tool_name=self.spec.name, content=str(bilgi))
        except httpx.HTTPError as hata:
            return ToolResult(
                tool_name=self.spec.name,
                content=f"YOTAY API hatası: {hata}",
                success=False,
            )

    @abstractmethod
    def _calistir(self, **params: Any) -> str:
        """Aracın asıl işi; bilinmeyen hat için HatBulunamadi fırlatabilir."""

    def _hat_getir(self, hat_no: str) -> dict[str, Any]:
        hatlar = self._kaynak.hatlari_getir()
        hat = next((h for h in hatlar if h["hat_no"] == hat_no), None)
        if hat is None:
            mevcut = ", ".join(h["hat_no"] for h in hatlar)
            raise HatBulunamadi(f"'{hat_no}' hattı bulunamadı. Mevcut hatlar: {mevcut}")
        return hat


class HatYogunluklariAraci(_YotayAraci):
    tool_id = "hat_yogunluklari"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="hat_yogunluklari",
            description=(
                "Tüm otobüs hatlarının anlık ortalama doluluğunu, yoğunluk seviyesini "
                "(seyrek/orta/yogun) ve araç sayısını listeler."
            ),
            parameters={"type": "object", "properties": {}, "required": []},
            category="yotay",
        )

    def _calistir(self) -> str:
        satirlar = [_hat_satiri(hat) for hat in self._kaynak.hatlari_getir()]
        return "\n".join(satirlar) or "Sistemde tanımlı hat yok."


class HatAnlikDurumAraci(_YotayAraci):
    tool_id = "hat_anlik_durum"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="hat_anlik_durum",
            description="Bir hattaki araçların anlık kişi sayısı, doluluk ve seviyesini verir.",
            parameters={
                "type": "object",
                "properties": {
                    "hat_no": {"type": "string", "description": "Hat numarası, örn: 34"},
                },
                "required": ["hat_no"],
            },
            category="yotay",
        )

    def _calistir(self, hat_no: str) -> str:
        hat = self._hat_getir(hat_no)
        araclar = self._kaynak.getir(f"/api/hatlar/{hat['hat_id']}/anlik")
        if not araclar:
            return f"{hat_no} hattında şu an aktif araç ölçümü yok."
        return f"{hat_no} hattı anlık durum:\n" + "\n".join(_arac_satiri(a) for a in araclar)


class HatTrendAraci(_YotayAraci):
    tool_id = "hat_trend"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="hat_trend",
            description="Bir hattın son saatlerdeki doluluk seyrini saatlik özetler.",
            parameters={
                "type": "object",
                "properties": {
                    "hat_no": {"type": "string", "description": "Hat numarası, örn: 34"},
                    "saat_sayisi": {
                        "type": "integer",
                        "description": "Kaç saat geriye bakılacağı, varsayılan "
                        f"{VARSAYILAN_TREND_SAATI}",
                    },
                },
                "required": ["hat_no"],
            },
            category="yotay",
        )

    def _calistir(self, hat_no: str, saat_sayisi: Any = VARSAYILAN_TREND_SAATI) -> str:
        hat = self._hat_getir(hat_no)
        try:
            saat = int(saat_sayisi)
        except (TypeError, ValueError):
            return f"saat_sayisi tam sayı olmalı (gelen: {saat_sayisi!r})."
        yol = f"/api/hatlar/{hat['hat_id']}/trend"
        noktalar = self._kaynak.getir(yol, _trend_parametreleri(saat))
        if not noktalar:
            return f"{hat_no} hattı için son {saat} saatte kayıt yok."
        govde = "\n".join(_trend_satiri(nokta) for nokta in noktalar)
        return f"{hat_no} hattı son {saat} saat:\n{govde}"


def varsayilan_araclar(kaynak: YotayVeriKaynagi) -> list[BaseTool]:
    return [HatYogunluklariAraci(kaynak), HatAnlikDurumAraci(kaynak), HatTrendAraci(kaynak)]
