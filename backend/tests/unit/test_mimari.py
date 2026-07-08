"""Mimari fitness testi: bağımlılık okları yalnızca içeri döner (plan Bölüm 4/12).

`domain/` yalnızca standart kütüphane + kendi modüllerini import edebilir;
SQLAlchemy, Redis, aiomqtt, FastAPI gibi altyapı kütüphaneleri yasaktır.
Kural AST taramasıyla doğrulanır — yasaklı import eklenirse bu test kırılır
(kabul kriteri #8). Faz 2'de `application/` katmanı da bu tabloya eklenecek.
"""

import ast
import sys
from collections.abc import Iterator
from pathlib import Path

UYGULAMA_KOKU = Path(__file__).resolve().parents[2] / "app"

# katman → import etmesine izin verilen app-içi kökler
KATMAN_IZINLERI: dict[str, set[str]] = {
    "domain": {"app.domain"},
}


def _importlar(dosya: Path) -> Iterator[str]:
    agac = ast.parse(dosya.read_text(encoding="utf-8"))
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.Import):
            yield from (ad.name for ad in dugum.names)
        elif isinstance(dugum, ast.ImportFrom) and dugum.module and dugum.level == 0:
            # Göreli importlar (level > 0) paket içidir; her zaman serbesttir.
            yield dugum.module


def _ihlaller(katman: str, izinli_app_kokleri: set[str]) -> list[str]:
    sonuc: list[str] = []
    for dosya in sorted((UYGULAMA_KOKU / katman).rglob("*.py")):
        for modul in _importlar(dosya):
            kok = modul.split(".")[0]
            if kok in sys.stdlib_module_names:
                continue
            app_ici_izinli = kok == "app" and any(
                modul == izinli or modul.startswith(izinli + ".")
                for izinli in izinli_app_kokleri
            )
            if app_ici_izinli:
                continue
            sonuc.append(f"{dosya.relative_to(UYGULAMA_KOKU)} → {modul}")
    return sonuc


def test_korunan_katmanlar_mevcut() -> None:
    for katman in KATMAN_IZINLERI:
        assert (UYGULAMA_KOKU / katman).is_dir(), f"app/{katman} katmanı bulunamadı"


def test_korunan_katmanlar_yalnizca_iceri_bakar() -> None:
    tum_ihlaller = {
        katman: ihlaller
        for katman, izinliler in KATMAN_IZINLERI.items()
        if (ihlaller := _ihlaller(katman, izinliler))
    }
    assert not tum_ihlaller, f"Yasaklı importlar bulundu: {tum_ihlaller}"
