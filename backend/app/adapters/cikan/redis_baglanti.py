"""Redis bağlantı yönetimi ve sağlık kontrolü."""

from redis.asyncio import Redis


def redis_istemcisi_olustur(redis_url: str) -> Redis:
    return Redis.from_url(redis_url)


async def redis_saglikli(istemci: Redis) -> bool:
    return bool(await istemci.ping())
