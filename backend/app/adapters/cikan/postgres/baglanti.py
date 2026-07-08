"""PostgreSQL bağlantı yönetimi, şema kurulumu ve sağlık kontrolü."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.adapters.cikan.postgres.tablolar import Taban


def motor_olustur(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url)


async def tablolari_olustur(motor: AsyncEngine) -> None:
    """Açılışta şemayı kurar (hackathon pragmatizmi: Alembic yerine create_all)."""
    async with motor.begin() as baglanti:
        await baglanti.run_sync(Taban.metadata.create_all)


async def postgres_saglikli(motor: AsyncEngine) -> bool:
    async with motor.connect() as baglanti:
        await baglanti.execute(text("SELECT 1"))
    return True
