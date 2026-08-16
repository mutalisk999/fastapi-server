#!/usr/bin/env python
# encoding: utf-8
from typing import Any, Optional

import redis
from redis import ConnectionPool
from redis.client import Redis
from utils.logger import logger

# Atomic INCR + EXPIRE-on-first so a rate-limit key can never outlive its window
# even if the EXPIRE step were to fail.
_INCR_EXPIRE_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""

class RedisClient(object):
    def __init__(self, url: str = "redis://127.0.0.1:6379/0", max_connections: int = 10,
                 socket_timeout: float = 3.0, socket_connect_timeout: float = 3.0):
        # Non-None timeouts prevent a stalled (but not down) Redis from blocking
        # requests indefinitely.
        self.client_pool: ConnectionPool = redis.ConnectionPool.from_url(
            url=url, max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
        )
        self.redis_client: Redis = redis.Redis(connection_pool=self.client_pool)
        self._connected = False
        # Only wraps the script; nothing is sent to Redis until it is invoked.
        self._limit_script = self.redis_client.register_script(_INCR_EXPIRE_SCRIPT)
        # Test connection lazily - don't block startup
        try:
            self.redis_client.ping()
            self._connected = True
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.warning(f"Redis not available at startup: {e}. Will retry on first operation.")

    def _ensure_connection(self):
        """Ensure Redis connection is available, retry if needed"""
        if not self._connected:
            try:
                self.redis_client.ping()
                self._connected = True
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                raise

    def get(self, key: str) -> Any:
        try:
            self._ensure_connection()
            return self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 0):
        try:
            self._ensure_connection()
            # Single SET with EX so the key can never outlive its TTL even if a
            # separate EXPIRE call were to fail.
            self.redis_client.set(key, value, ex=expire if expire > 0 else None)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        """Atomically increment a key and return the new value.

        Unlike most methods here, this raises on Redis failure so callers
        (e.g. rate limiting) can fall back to an in-memory implementation.
        """
        self._ensure_connection()
        return self.redis_client.incr(key, amount)

    def incr_with_expire(self, key: str, expire_seconds: int) -> int:
        """Atomically increment a key and return the new value, setting the
        key's TTL on the first hit. The INCR and EXPIRE run as one Lua script,
        so the key can never persist without a TTL. Raises on Redis failure.
        """
        self._ensure_connection()
        return self._limit_script(keys=[key], args=[expire_seconds])

    def delete(self, key: str):
        try:
            self._ensure_connection()
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def expire(self, key: str, expire: int):
        try:
            self._ensure_connection()
            self.redis_client.expire(key, expire)
            return True
        except Exception as e:
            logger.error(f"Redis expire error: {e}")
            return False

    # Hash operations
    def hset(self, key: str, field: str, value: Any) -> bool:
        try:
            self._ensure_connection()
            self.redis_client.hset(key, field, value)
            return True
        except Exception as e:
            logger.error(f"Redis hset error: {e}")
            return False

    def hget(self, key: str, field: str) -> Any:
        try:
            self._ensure_connection()
            return self.redis_client.hget(key, field)
        except Exception as e:
            logger.error(f"Redis hget error: {e}")
            return None

    def hgetall(self, key: str) -> dict:
        try:
            self._ensure_connection()
            return self.redis_client.hgetall(key)
        except Exception as e:
            logger.error(f"Redis hgetall error: {e}")
            return {}

    def hdel(self, key: str, field: str) -> bool:
        try:
            self._ensure_connection()
            self.redis_client.hdel(key, field)
            return True
        except Exception as e:
            logger.error(f"Redis hdel error: {e}")
            return False

    def hexists(self, key: str, field: str) -> bool:
        try:
            self._ensure_connection()
            return self.redis_client.hexists(key, field)
        except Exception as e:
            logger.error(f"Redis hexists error: {e}")
            return False

    # List operations
    def lpush(self, key: str, *values) -> int:
        try:
            self._ensure_connection()
            return self.redis_client.lpush(key, *values)
        except Exception as e:
            logger.error(f"Redis lpush error: {e}")
            return 0

    def rpush(self, key: str, *values) -> int:
        try:
            self._ensure_connection()
            return self.redis_client.rpush(key, *values)
        except Exception as e:
            logger.error(f"Redis rpush error: {e}")
            return 0

    def lpop(self, key: str) -> Any:
        try:
            self._ensure_connection()
            return self.redis_client.lpop(key)
        except Exception as e:
            logger.error(f"Redis lpop error: {e}")
            return None

    def rpop(self, key: str) -> Any:
        try:
            self._ensure_connection()
            return self.redis_client.rpop(key)
        except Exception as e:
            logger.error(f"Redis rpop error: {e}")
            return None

    def lrange(self, key: str, start: int, end: int) -> list:
        try:
            self._ensure_connection()
            return self.redis_client.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Redis lrange error: {e}")
            return []

    def llen(self, key: str) -> int:
        try:
            self._ensure_connection()
            return self.redis_client.llen(key)
        except Exception as e:
            logger.error(f"Redis llen error: {e}")
            return 0

    # Set operations
    def sadd(self, key: str, *values) -> int:
        try:
            self._ensure_connection()
            return self.redis_client.sadd(key, *values)
        except Exception as e:
            logger.error(f"Redis sadd error: {e}")
            return 0

    def srem(self, key: str, *values) -> int:
        try:
            self._ensure_connection()
            return self.redis_client.srem(key, *values)
        except Exception as e:
            logger.error(f"Redis srem error: {e}")
            return 0

    def smembers(self, key: str) -> set:
        try:
            self._ensure_connection()
            return self.redis_client.smembers(key)
        except Exception as e:
            logger.error(f"Redis smembers error: {e}")
            return set()

    def sismember(self, key: str, value: Any) -> bool:
        try:
            self._ensure_connection()
            return self.redis_client.sismember(key, value)
        except Exception as e:
            logger.error(f"Redis sismember error: {e}")
            return False

    def scard(self, key: str) -> int:
        try:
            self._ensure_connection()
            return self.redis_client.scard(key)
        except Exception as e:
            logger.error(f"Redis scard error: {e}")
            return 0

    # ZSet operations
    def zadd(self, key: str, mapping: dict) -> int:
        try:
            self._ensure_connection()
            return self.redis_client.zadd(key, mapping)
        except Exception as e:
            logger.error(f"Redis zadd error: {e}")
            return 0

    def zrem(self, key: str, *values) -> int:
        try:
            self._ensure_connection()
            return self.redis_client.zrem(key, *values)
        except Exception as e:
            logger.error(f"Redis zrem error: {e}")
            return 0

    def zrange(self, key: str, start: int, end: int, withscores: bool = False) -> list:
        try:
            self._ensure_connection()
            return self.redis_client.zrange(key, start, end, withscores=withscores)
        except Exception as e:
            logger.error(f"Redis zrange error: {e}")
            return []

    def zrangebyscore(self, key: str, min_score: float, max_score: float, withscores: bool = False) -> list:
        try:
            self._ensure_connection()
            return self.redis_client.zrangebyscore(key, min_score, max_score, withscores=withscores)
        except Exception as e:
            logger.error(f"Redis zrangebyscore error: {e}")
            return []

    def zscore(self, key: str, value: Any) -> Optional[float]:
        try:
            self._ensure_connection()
            return self.redis_client.zscore(key, value)
        except Exception as e:
            logger.error(f"Redis zscore error: {e}")
            return None
