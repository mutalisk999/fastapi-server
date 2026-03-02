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
