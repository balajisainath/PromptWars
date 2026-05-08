import json
from typing import Optional, Any
import redis.asyncio as aioredis
from .config import get_settings

settings = get_settings()

_pool: Optional[aioredis.ConnectionPool] = None


def get_redis_pool() -> aioredis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=50,
            decode_responses=True,
        )
    return _pool


def get_redis_client() -> aioredis.Redis:
    return aioredis.Redis(connection_pool=get_redis_pool())


async def get_cached(key: str) -> Optional[str]:
    client = get_redis_client()
    return await client.get(key)


async def get_cached_json(key: str) -> Optional[Any]:
    raw = await get_cached(key)
    if raw is None:
        return None
    return json.loads(raw)


async def set_cached(key: str, value: str, ttl: int = 3600) -> None:
    client = get_redis_client()
    await client.setex(key, ttl, value)


async def set_cached_json(key: str, value: Any, ttl: int = 3600) -> None:
    await set_cached(key, json.dumps(value), ttl)


async def delete_pattern(pattern: str) -> int:
    client = get_redis_client()
    keys = await client.keys(pattern)
    if not keys:
        return 0
    return await client.delete(*keys)


async def close_redis():
    global _pool
    if _pool:
        await _pool.disconnect()
        _pool = None
