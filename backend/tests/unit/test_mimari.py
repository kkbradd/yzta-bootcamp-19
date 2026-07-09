"""Mimari fitness testi: bağımlılık okları yalnızca içeri döner (plan Bölüm 4/12).

Korunan katmanlar yalnızca standart kütüphane + izinli app-içi modülleri
import edebilir; SQLAlchemy, Redis, aiomqtt, FastAPI gibi altyapı
kütüphaneleri yasaktır. Kural AST taramasıyla doğrulanır — yasaklı import
eklenirse bu test kırılır (kabul kriteri #8). Göreli importlar dosyanın
paket yoluna göre mutlak yola çözülür; katmandan dışarı tırmanan
`from .. import x` biçimleri de aynı izin listesinden geçer.
"""

import ast
import sys
from collections.abc import Iterator
from pathlib import Path

UYGULAMA_KOKU = Path(__file__).resolve().parents[2] / "app"

# katman → import etmesine izin verilen app-içi kökler
KATMAN_IZINLERI: dict[str, set[str]] = {
    "domain": {"app.domain"},
    "ports": {"app.domain", "app.ports"},
    "application": {"app.domain", "app.ports", "app.application"},
}


def _modul_paketi(dosya: Path) -> tuple[str, ...]:
    """Dosyanın içinde bulunduğu paketin yolu: app/domain/x.py → ('app', 'domain')."""
    parcalar = dosya.relative_to(UYGULAMA_KOKU.parent).with_suffix("").parts
    if parcalar[-1] == "__init__":
        parcalar = parcalar[:-1]
    return parcalar[:-1]


def _importlar(dosya: Path) -> Iterator[str]:
    agac = ast.parse(dosya.read_text(encoding="utf-8"))
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.Import):
            yield from (ad.name for ad in dugum.names)
        elif isinstance(dugum, ast.ImportFrom):
            if dugum.level == 0:
                if dugum.module:
                    yield dugum.module
            else:
                # Göreli importu mutlak yola çöz: `from .. import x` katmandan
                # dışarı tırmanabilir, izin listesinden muaf tutulamaz.
                taban = _modul_paketi(dosya)
                if dugum.level > 1:
                    taban = taban[: -(dugum.level - 1)]
                ekler = tuple(dugum.module.split(".")) if dugum.module else ()
                yield ".".join(taban + ekler)


def _ihlaller(katman: str, izinli_app_kokleri: set[str]) -> list[str]:
    sonuc: list[str] = []
    for dosya in sorted((UYGULAMA_KOKU / katman).rglob("*.py")):
        for modul in _importlar(dosya):
            kok = modul.split(".")[0]
            if kok in sys.stdlib_module_names:
                continue
            app_ici_izinli = kok == "app" and any(
                modul == izinli or modul.startswith(izinli + ".") for izinli in izinli_app_kokleri
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
