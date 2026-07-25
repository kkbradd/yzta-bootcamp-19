"""GET/POST /api/uyarilar birim testleri — altyapısız, sahte adaptörlerle."""

from datetime import UTC, datetime

from httpx import ASGITransport, AsyncClient

from app.adapters.giren.rest.bagimliliklar import uyari_deposu_getir, uyari_uret_getir
from app.domain.modeller import Uyari
from app.main import uygulama_olustur

UYARI = Uyari(
    id=1,
    hat_id=2,
    ortalama_doluluk=0.85,
    ortalama_kisi=76.0,
    uyari_metni="2 numaralı hat şu anda yoğun, ek sefer değerlendirilebilir.",
    gerekce="Son 3 saatte ortalama doluluk %85.",
    olusturulma_zamani=datetime(2026, 7, 13, tzinfo=UTC),
)


class SahteUyariDeposu:
    async def son_uyarilar(self, limit: int = 50) -> list[Uyari]:
        return [UYARI][:limit]


class SahteUyariUretUseCase:
    async def calistir(self) -> list[Uyari]:
        return [UYARI]


def _istemci() -> AsyncClient:
    uygulama = uygulama_olustur()
    uygulama.dependency_overrides[uyari_deposu_getir] = lambda: SahteUyariDeposu()
    uygulama.dependency_overrides[uyari_uret_getir] = lambda: SahteUyariUretUseCase()
    return AsyncClient(transport=ASGITransport(app=uygulama), base_url="http://test")


async def test_uyarilar_listelenir() -> None:
    async with _istemci() as istemci:
        yanit = await istemci.get("/api/uyarilar")

    assert yanit.status_code == 200
    (uyari,) = yanit.json()
    assert uyari["hat_id"] == 2
    assert uyari["uyari_metni"] == UYARI.uyari_metni


async def test_manuel_tetikleme_202_doner() -> None:
    async with _istemci() as istemci:
        yanit = await istemci.post("/api/uyarilar/uret")

    assert yanit.status_code == 202
    (uyari,) = yanit.json()
    assert uyari["gerekce"] == UYARI.gerekce
