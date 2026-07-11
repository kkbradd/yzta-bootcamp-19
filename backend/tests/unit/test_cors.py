"""CORSMiddleware birim testleri — altyapı ve lifespan gerektirmez.

CORS başlıkları global middleware ile eklenir; bu yüzden test için
altyapıya (PostgreSQL/Redis/MQTT) bağlı olmayan `/openapi.json` ucu ve
preflight `OPTIONS` isteği kullanılır. Kabul kriteri #9 gereği container'sız geçer.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import uygulama_olustur

_IZINLI = "http://localhost:3000"
_IZINSIZ = "http://kotu.example"


async def _get(yol: str, origin: str):
    uygulama = uygulama_olustur()
    transport = ASGITransport(app=uygulama)
    async with AsyncClient(transport=transport, base_url="http://test") as istemci:
        return await istemci.get(yol, headers={"origin": origin})


async def test_izinli_origin_acao_ve_credentials_basligi_alir() -> None:
    yanit = await _get("/openapi.json", _IZINLI)

    assert yanit.headers.get("access-control-allow-origin") == _IZINLI
    assert yanit.headers.get("access-control-allow-credentials") == "true"


async def test_izinsiz_origin_acao_basligi_almaz() -> None:
    yanit = await _get("/openapi.json", _IZINSIZ)

    assert "access-control-allow-origin" not in yanit.headers


async def test_preflight_options_izinli_origine_izin_verir() -> None:
    uygulama = uygulama_olustur()
    transport = ASGITransport(app=uygulama)
    async with AsyncClient(transport=transport, base_url="http://test") as istemci:
        yanit = await istemci.options(
            "/api/hatlar",
            headers={
                "origin": _IZINLI,
                "access-control-request-method": "GET",
            },
        )

    assert yanit.status_code == 200
    assert yanit.headers.get("access-control-allow-origin") == _IZINLI
    assert "GET" in yanit.headers.get("access-control-allow-methods", "")


def test_joker_origin_credentials_ile_acilista_patlar(monkeypatch: pytest.MonkeyPatch) -> None:
    # allow_credentials=True ile "*" origin tarayıcılarca reddedilir; yanlış
    # yapılandırma sessizce prod'a sızmasın diye açılışta ValueError beklenir.
    monkeypatch.setenv("CORS_IZINLI_ORIGINLER", "*")

    with pytest.raises(ValueError):
        uygulama_olustur()
