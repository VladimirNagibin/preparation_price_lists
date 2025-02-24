from typing import Any

from redis.asyncio import Redis

redis: Redis | None = None


class RedisClient:
    def __init__(self, db: Redis | None):
        self.redis = db

    async def get(self, name: Any) -> Any:
        return await self.redis.get(name)

    async def set(self, name: Any, value: Any, ex: int | None = None) -> None:
        await self.redis.set(name, value, ex=ex)

    async def delete(self, name: Any) -> None:
        await self.redis.delete(name)

    async def sadd(self, name: Any, values: Any) -> None:
        await self.redis.sadd(name, values)

    async def check_invalid_token(
        self, name: str = "invalid_token", value: Any = None
    ) -> bool:
        return await self.redis.sismember(name, value)


async def get_redis() -> RedisClient:
    return RedisClient(redis)