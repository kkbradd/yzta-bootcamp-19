"""OturumAc use-case birim testleri — SAHTE (in-memory) adaptörlerle."""

from app.application.oturum_ac import OturumAc
from app.domain.modeller import Kullanici

KULLANICI = Kullanici(id=1, eposta="admin@demo.com", sifre_hash="hash:admin123")


class SahteKullaniciDeposu:
    def __init__(self, kullanicilar: list[Kullanici] = ()) -> None:
        self._kullanicilar = {k.eposta: k for k in kullanicilar}

    async def epostaya_gore_bul(self, eposta: str) -> Kullanici | None:
        return self._kullanicilar.get(eposta)


class SahteSifreleyici:
    """Basit eşitlik: sifre_hash 'hash:<duz_sifre>' formatında varsayılır."""

    def dogrula(self, duz_sifre: str, sifre_hash: str) -> bool:
        return sifre_hash == f"hash:{duz_sifre}"


class SahteTokenUreticisi:
    def uret(self, kullanici_id: int, eposta: str) -> str:
        return f"sahte-token-{kullanici_id}"


def _oturum_ac(kullanicilar: list[Kullanici] = ()) -> OturumAc:
    return OturumAc(
        kullanici_deposu=SahteKullaniciDeposu(kullanicilar),
        sifreleyici=SahteSifreleyici(),
        token_uretici=SahteTokenUreticisi(),
    )


async def test_dogru_bilgilerle_token_doner() -> None:
    use_case = _oturum_ac([KULLANICI])

    token = await use_case.calistir("admin@demo.com", "admin123")

    assert token == "sahte-token-1"


async def test_yanlis_sifre_none_doner() -> None:
    use_case = _oturum_ac([KULLANICI])

    token = await use_case.calistir("admin@demo.com", "yanlis-sifre")

    assert token is None


async def test_kayitsiz_eposta_none_doner() -> None:
    use_case = _oturum_ac([KULLANICI])

    token = await use_case.calistir("olmayan@demo.com", "admin123")

    assert token is None
