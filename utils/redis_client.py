#!/usr/bin/env python
# encoding: utf-8
from typing import Any, Optional

import redis
from redis import ConnectionPool
from redis.client import Redis, StrictRedis
from utils.logger import logger

class RedisClient(object):
    def __init__(self, url: str = "redis://127.0.0.1:6379/0", max_connections: int = 10):
        self.client_pool: ConnectionPool = redis.ConnectionPool.from_url(url=url, max_connections=max_connections)
        self.redis_client: StrictRedis = redis.StrictRedis(connection_pool=self.client_pool)
        # Test connection on initialization
        try:
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to establish Redis connection: {e}")

    def get(self, key: str) -> Any:
        try:
            return self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 0):
        try:
            self.redis_client.set(key, value)
            if expire > 0:
                self.redis_client.expire(key, expire)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def delete(self, key: str):
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def expire(self, key: str, expire: int):
        try:
            self.redis_client.expire(key, expire)
            return True
        except Exception as e:
            logger.error(f"Redis expire error: {e}")
            return False
    
    # Hash operations
    def hset(self, key: str, field: str, value: Any) -> bool:
        try:
            self.redis_client.hset(key, field, value)
            return True
        except Exception as e:
            logger.error(f"Redis hset error: {e}")
            return False
    
    def hget(self, key: str, field: str) -> Any:
        try:
            return self.redis_client.hget(key, field)
        except Exception as e:
            logger.error(f"Redis hget error: {e}")
            return None
    
    def hgetall(self, key: str) -> dict:
        try:
            return self.redis_client.hgetall(key)
        except Exception as e:
            logger.error(f"Redis hgetall error: {e}")
            return {}
    
    def hdel(self, key: str, field: str) -> bool:
        try:
            self.redis_client.hdel(key, field)
            return True
        except Exception as e:
            logger.error(f"Redis hdel error: {e}")
            return False
    
    def hexists(self, key: str, field: str) -> bool:
        try:
            return self.redis_client.hexists(key, field)
        except Exception as e:
            logger.error(f"Redis hexists error: {e}")
            return False
    
    # List operations
    def lpush(self, key: str, *values) -> int:
        try:
            return self.redis_client.lpush(key, *values)
        except Exception as e:
            logger.error(f"Redis lpush error: {e}")
            return 0
    
    def rpush(self, key: str, *values) -> int:
        try:
            return self.redis_client.rpush(key, *values)
        except Exception as e:
            logger.error(f"Redis rpush error: {e}")
            return 0
    
    def lpop(self, key: str) -> Any:
        try:
            return self.redis_client.lpop(key)
        except Exception as e:
            logger.error(f"Redis lpop error: {e}")
            return None
    
    def rpop(self, key: str) -> Any:
        try:
            return self.redis_client.rpop(key)
        except Exception as e:
            logger.error(f"Redis rpop error: {e}")
            return None
    
    def lrange(self, key: str, start: int, end: int) -> list:
        try:
            return self.redis_client.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Redis lrange error: {e}")
            return []
    
    def llen(self, key: str) -> int:
        try:
            return self.redis_client.llen(key)
        except Exception as e:
            logger.error(f"Redis llen error: {e}")
            return 0
    
    # Set operations
    def sadd(self, key: str, *values) -> int:
        try:
            return self.redis_client.sadd(key, *values)
        except Exception as e:
            logger.error(f"Redis sadd error: {e}")
            return 0
    
    def srem(self, key: str, *values) -> int:
        try:
            return self.redis_client.srem(key, *values)
        except Exception as e:
            logger.error(f"Redis srem error: {e}")
            return 0
    
    def smembers(self, key: str) -> set:
        try:
            return self.redis_client.smembers(key)
        except Exception as e:
            logger.error(f"Redis smembers error: {e}")
            return set()
    
    def sismember(self, key: str, value: Any) -> bool:
        try:
            return self.redis_client.sismember(key, value)
        except Exception as e:
            logger.error(f"Redis sismember error: {e}")
            return False
    
    def scard(self, key: str) -> int:
        try:
            return self.redis_client.scard(key)
        except Exception as e:
            logger.error(f"Redis scard error: {e}")
            return 0
    
    # ZSet operations
    def zadd(self, key: str, mapping: dict) -> int:
        try:
            return self.redis_client.zadd(key, mapping)
        except Exception as e:
            logger.error(f"Redis zadd error: {e}")
            return 0
    
    def zrem(self, key: str, *values) -> int:
        try:
            return self.redis_client.zrem(key, *values)
        except Exception as e:
            logger.error(f"Redis zrem error: {e}")
            return 0
    
    def zrange(self, key: str, start: int, end: int, withscores: bool = False) -> list:
        try:
            return self.redis_client.zrange(key, start, end, withscores=withscores)
        except Exception as e:
            logger.error(f"Redis zrange error: {e}")
            return []
    
    def zrangebyscore(self, key: str, min_score: float, max_score: float, withscores: bool = False) -> list:
        try:
            return self.redis_client.zrangebyscore(key, min_score, max_score, withscores=withscores)
        except Exception as e:
            logger.error(f"Redis zrangebyscore error: {e}")
            return []
    
    def zscore(self, key: str, value: Any) -> Optional[float]:
        try:
            return self.redis_client.zscore(key, value)
        except Exception as e:
            logger.error(f"Redis zscore error: {e}")
            return None
