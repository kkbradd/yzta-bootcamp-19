"""GET /api/saglik ucunun birim testleri.

Altyapı (PostgreSQL, Redis, MQTT) gerektirmez: sahte sağlık kontrolleri
FastAPI `dependency_overrides` ile enjekte edilir; lifespan'daki gerçek
adaptör kablolaması hiç çalışmaz. Kabul kriteri #9 gereği container'sız geçer.
"""

from httpx import ASGITransport, AsyncClient

from app.adapters.giren.rest.saglik import SaglikKontrolu, saglik_kontrollerini_getir
from app.main import uygulama_olustur


async def _saglikli() -> bool:
    return True


async def _arizali() -> bool:
    return False


async def _patlayan() -> bool:
    raise ConnectionError("bağlantı koptu")


async def _saglik_yaniti(kontroller: dict[str, SaglikKontrolu]) -> tuple[int, dict]:
    uygulama = uygulama_olustur()
    uygulama.dependency_overrides[saglik_kontrollerini_getir] = lambda: kontroller
    transport = ASGITransport(app=uygulama)
    async with AsyncClient(transport=transport, base_url="http://test") as istemci:
        yanit = await istemci.get("/api/saglik")
    return yanit.status_code, yanit.json()


async def test_tum_bagimliliklar_saglikliyken_ok_doner() -> None:
    durum_kodu, govde = await _saglik_yaniti(
        {"postgres": _saglikli, "redis": _saglikli, "mqtt": _saglikli}
    )

    assert durum_kodu == 200
    assert govde["durum"] == "ok"
    assert govde["bagimliliklar"] == {"postgres": "ok", "redis": "ok", "mqtt": "ok"}


async def test_bir_bagimlilik_arizaliyken_503_ve_hata_doner() -> None:
    durum_kodu, govde = await _saglik_yaniti(
        {"postgres": _saglikli, "redis": _arizali, "mqtt": _saglikli}
    )

    assert durum_kodu == 503
    assert govde["durum"] == "hata"
    assert govde["bagimliliklar"]["redis"] == "hata"
    assert govde["bagimliliklar"]["postgres"] == "ok"


async def test_kontrol_istisna_firlatirsa_uc_dusmez_hata_sayilir() -> None:
    durum_kodu, govde = await _saglik_yaniti(
        {"postgres": _patlayan, "redis": _saglikli, "mqtt": _saglikli}
    )

    assert durum_kodu == 503
    assert govde["bagimliliklar"]["postgres"] == "hata"
