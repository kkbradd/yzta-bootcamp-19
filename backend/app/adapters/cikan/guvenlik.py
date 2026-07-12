"""Şifre hash'leme ve JWT üretimi — somut kriptografi yalnız burada yaşar."""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.ports.kimlik import SifreleyiciPort, TokenUreticiPort


def sifre_hashle(duz_sifre: str) -> str:
    """Seed script'i için: düz şifreyi bcrypt hash'ine çevirir."""
    return bcrypt.hashpw(duz_sifre.encode(), bcrypt.gensalt()).decode()


class BcryptSifreleyici(SifreleyiciPort):
    def dogrula(self, duz_sifre: str, sifre_hash: str) -> bool:
        return bcrypt.checkpw(duz_sifre.encode(), sifre_hash.encode())


class JwtTokenUretici(TokenUreticiPort):
    def __init__(self, gizli_anahtar: str, gecerlilik_sn: int) -> None:
        self._gizli_anahtar = gizli_anahtar
        self._gecerlilik_sn = gecerlilik_sn

    def uret(self, kullanici_id: int, eposta: str) -> str:
        simdi = datetime.now(UTC)
        yuk = {
            "sub": str(kullanici_id),
            "eposta": eposta,
            "iat": simdi,
            "exp": simdi + timedelta(seconds=self._gecerlilik_sn),
        }
        return jwt.encode(yuk, self._gizli_anahtar, algorithm="HS256")
