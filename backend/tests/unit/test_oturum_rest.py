"""POST /api/oturum birim testleri — altyapısız, sahte use-case ile."""

from httpx import ASGITransport, AsyncClient

from app.adapters.giren.rest.bagimliliklar import oturum_ac_use_case_getir
from app.main import uygulama_olustur


class SahteOturumAc:
    async def calistir(self, eposta: str, sifre: str) -> str | None:
        if eposta == "admin@demo.com" and sifre == "admin123":
            return "sahte-token"
        return None


def _istemci() -> AsyncClient:
    uygulama = uygulama_olustur()
    uygulama.dependency_overrides[oturum_ac_use_case_getir] = lambda: SahteOturumAc()
    return AsyncClient(transport=ASGITransport(app=uygulama), base_url="http://test")


async def test_dogru_bilgilerle_200_ve_token_doner() -> None:
    async with _istemci() as istemci:
        yanit = await istemci.post(
            "/api/oturum", json={"eposta": "admin@demo.com", "sifre": "admin123"}
        )

    assert yanit.status_code == 200
    govde = yanit.json()
    assert govde["erisim_tokeni"] == "sahte-token"
    assert govde["token_tipi"] == "bearer"


async def test_yanlis_bilgilerle_401_doner() -> None:
    async with _istemci() as istemci:
        yanit = await istemci.post(
            "/api/oturum", json={"eposta": "admin@demo.com", "sifre": "yanlis"}
        )

    assert yanit.status_code == 401


async def test_eksik_alan_422_doner() -> None:
    async with _istemci() as istemci:
        yanit = await istemci.post("/api/oturum", json={"eposta": "admin@demo.com"})

    assert yanit.status_code == 422
