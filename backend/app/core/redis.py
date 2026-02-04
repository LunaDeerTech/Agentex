"""Redis connection management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.sentinel import Sentinel

from app.core.config import settings

# Connection pool
_pool: ConnectionPool | None = None
_client: Redis | None = None
_sentinel: Sentinel | None = None


def _parse_sentinel_hosts() -> list[tuple[str, int]]:
    """Parse sentinel hosts from settings.REDIS_SENTINEL_HOSTS."""
    hosts: list[tuple[str, int]] = []
    if not settings.REDIS_SENTINEL_HOSTS:
        return hosts

    for item in settings.REDIS_SENTINEL_HOSTS.split(","):
        host = item.strip()
        if not host:
            continue
        if ":" in host:
            host_name, port = host.split(":", 1)
            hosts.append((host_name.strip(), int(port)))
        else:
            hosts.append((host, 26379))
    return hosts


async def init_redis() -> Redis:
    """Initialize Redis connection pool and client."""
    global _pool, _client, _sentinel

    # Sentinel mode (optional)
    sentinel_hosts = _parse_sentinel_hosts()
    if sentinel_hosts and settings.REDIS_SENTINEL_SERVICE_NAME:
        _sentinel = Sentinel(
            sentinel_hosts,
            password=settings.REDIS_SENTINEL_PASSWORD,
            socket_timeout=2,
        )
        _client = _sentinel.master_for(
            settings.REDIS_SENTINEL_SERVICE_NAME,
            decode_responses=True,
        )
        await _client.ping()
        return _client

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
    global _pool, _client, _sentinel

    if _client:
        await _client.close()
        _client = None

    if _pool:
        await _pool.disconnect()
        _pool = None

    _sentinel = None


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


async def health_check() -> bool:
    """Check Redis health status."""
    try:
        client = get_redis()
        return await client.ping() is True
    except Exception:
        return False


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

    def __init__(self, prefix: str = "agentex", default_ttl: int | None = None):
        self.prefix = prefix
        self.default_ttl = default_ttl

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
        ttl = expire if expire is not None else self.default_ttl
        return await client.set(self._make_key(key), value, ex=ttl)

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
cache = RedisCache(default_ttl=settings.REDIS_DEFAULT_TTL)
