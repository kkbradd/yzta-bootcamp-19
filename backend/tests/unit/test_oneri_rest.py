"""GET/POST /api/oneriler birim testleri — altyapısız, sahte adaptörlerle."""

from datetime import UTC, datetime

from httpx import ASGITransport, AsyncClient

from app.adapters.giren.rest.bagimliliklar import oneri_deposu_getir, oneri_uret_getir
from app.domain.modeller import Oneri
from app.main import uygulama_olustur

ONERI = Oneri(
    id=1,
    hat_id=1,
    gun_no=1,
    saat_baslangic=8,
    saat_bitis=10,
    ortalama_doluluk=0.88,
    karsilastirma_ortalama_doluluk=0.42,
    oneri_metni="Pazartesi 08-10 arası sefer sıklığını artırmayı düşünün.",
    gerekce="Diğer günlere göre belirgin sapma var.",
    olusturulma_zamani=datetime(2026, 7, 13, tzinfo=UTC),
)


class SahteOneriDeposu:
    async def son_oneriler(self, limit: int = 50) -> list[Oneri]:
        return [ONERI][:limit]


class SahteOneriUretUseCase:
    async def calistir(self) -> list[Oneri]:
        return [ONERI]


def _istemci() -> AsyncClient:
    uygulama = uygulama_olustur()
    uygulama.dependency_overrides[oneri_deposu_getir] = lambda: SahteOneriDeposu()
    uygulama.dependency_overrides[oneri_uret_getir] = lambda: SahteOneriUretUseCase()
    return AsyncClient(transport=ASGITransport(app=uygulama), base_url="http://test")


async def test_oneriler_listelenir() -> None:
    async with _istemci() as istemci:
        yanit = await istemci.get("/api/oneriler")

    assert yanit.status_code == 200
    (oneri,) = yanit.json()
    assert oneri["hat_id"] == 1
    assert oneri["oneri_metni"] == ONERI.oneri_metni


async def test_manuel_tetikleme_202_doner() -> None:
    async with _istemci() as istemci:
        yanit = await istemci.post("/api/oneriler/uret")

    assert yanit.status_code == 202
    (oneri,) = yanit.json()
    assert oneri["gerekce"] == ONERI.gerekce
