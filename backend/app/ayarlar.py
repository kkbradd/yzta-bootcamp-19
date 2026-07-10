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
