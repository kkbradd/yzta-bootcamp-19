"""Giriş akışı: eposta + şifreyi doğrular, başarılıysa erişim tokeni üretir."""

from dataclasses import dataclass

from app.ports.kimlik import KullaniciDeposuPort, SifreleyiciPort, TokenUreticiPort


@dataclass(frozen=True, slots=True)
class OturumAc:
    kullanici_deposu: KullaniciDeposuPort
    sifreleyici: SifreleyiciPort
    token_uretici: TokenUreticiPort

    async def calistir(self, eposta: str, sifre: str) -> str | None:
        """Girişi doğrular; başarılıysa token, başarısızsa None döner.

        Kayıtsız eposta ile hatalı şifre ayırt edilmez (enumeration önlemi).
        """
        kullanici = await self.kullanici_deposu.epostaya_gore_bul(eposta)
        if kullanici is None:
            return None
        if not self.sifreleyici.dogrula(sifre, kullanici.sifre_hash):
            return None
        return self.token_uretici.uret(kullanici.id, kullanici.eposta)
