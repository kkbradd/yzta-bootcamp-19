"""Uygulama yapılandırması — tüm eşikler ve bağlantı bilgileri .env'den okunur."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Ayarlar(BaseSettings):
    """Ortam değişkenlerinden yüklenen uygulama ayarları.

    Varsayılanlar yerel geliştirme içindir; compose ortamında servis adları
    ortam değişkenleriyle geçersiz kılınır (bkz. docker-compose.yml).
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://hat01:hat01@localhost:5432/hat01"
    redis_url: str = "redis://localhost:6379/0"
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883

    seviye_seyrek_ust: float = 0.40
    seviye_orta_ust: float = 0.70

    redis_arac_ttl_sn: int = 30
    redis_hat_ttl_sn: int = 60

    # Panel farklı origin'den (farklı port) çağırırsa tarayıcı CORS ister.
    # Virgülle ayrılmış origin listesi; prod'da tek origin (reverse proxy)
    # kullanılıyorsa boş bırakılabilir.
    cors_izinli_originler: str = "http://localhost:3000,http://localhost:5173"

    # Varsayılan yalnız geliştirme içindir; prod'da .env ile geçersiz kılınmalı.
    jwt_gizli_anahtar: str = "gelistirme-ortami-gizli-anahtari-degistir"
    jwt_gecerlilik_sn: int = 3600 * 8

    # Öneri motoru: haftalık örüntü tespiti + LLM yorumlama (bkz. app/application/oneri_uret.py).
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    oneri_calisma_gunu: int = 0  # Pazartesi (datetime.weekday())
    oneri_calisma_saati: int = 6
    oneri_gun_pencere: int = 30

    # Son Uyarılar akışı: son N saatlik ham veriye bakıp yoğun hatlar için anlık LLM uyarısı.
    uyari_saat_pencere: int = 3
    uyari_calisma_periyodu_sn: int = 10800  # 3 saat

    @property
    def cors_originleri(self) -> list[str]:
        return [o.strip() for o in self.cors_izinli_originler.split(",") if o.strip()]
