"""PostgreSQL bağlantı yönetimi ve sağlık kontrolü."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def motor_olustur(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url)


async def postgres_saglikli(motor: AsyncEngine) -> bool:
    async with motor.connect() as baglanti:
        await baglanti.execute(text("SELECT 1"))
    return True
