"""Redis connection management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings

# Connection pool
_pool: ConnectionPool | None = None
_client: Redis | None = None


async def init_redis() -> Redis:
    """Initialize Redis connection pool and client."""
    global _pool, _client
    
    _pool = ConnectionPool.from_url(
        str(settings.REDIS_URL),
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        decode_responses=True,
    )
    _client = Redis(connection_pool=_pool)
    
    # Test connection
    await _client.ping()
    
    return _client


async def close_redis() -> None:
    """Close Redis connections."""
    global _pool, _client
    
    if _client:
        await _client.close()
        _client = None
    
    if _pool:
        await _pool.disconnect()
        _pool = None


def get_redis() -> Redis:
    """
    Get Redis client instance.
    
    Usage:
        @router.get("/cache/{key}")
        async def get_cache(key: str, redis: Redis = Depends(get_redis)):
            return await redis.get(key)
    """
    if _client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return _client


@asynccontextmanager
async def get_redis_context() -> AsyncGenerator[Redis, None]:
    """
    Context manager for Redis client outside of request context.
    
    Usage:
        async with get_redis_context() as redis:
            await redis.set("key", "value")
    """
    client = get_redis()
    try:
        yield client
    finally:
        pass  # Connection is managed by the pool


class RedisCache:
    """Redis cache utility class."""

    def __init__(self, prefix: str = "agentex"):
        self.prefix = prefix

    def _make_key(self, key: str) -> str:
        """Create a prefixed cache key."""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> str | None:
        """Get a value from cache."""
        client = get_redis()
        return await client.get(self._make_key(key))

    async def set(
        self,
        key: str,
        value: str,
        expire: int | None = None,
    ) -> bool:
        """Set a value in cache with optional expiration (seconds)."""
        client = get_redis()
        return await client.set(self._make_key(key), value, ex=expire)

    async def delete(self, key: str) -> int:
        """Delete a key from cache."""
        client = get_redis()
        return await client.delete(self._make_key(key))

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        client = get_redis()
        return await client.exists(self._make_key(key)) > 0

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on a key."""
        client = get_redis()
        return await client.expire(self._make_key(key), seconds)


# Default cache instance
cache = RedisCache()
