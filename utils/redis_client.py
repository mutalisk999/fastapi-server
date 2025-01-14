#!/usr/bin/env python
# encoding: utf-8
from typing import Any, Optional

import redis
from redis import ConnectionPool
from redis.client import Redis, StrictRedis


class RedisClient(object):
    def __init__(self, url: str = "redis://127.0.0.1:6379/0", max_connections: int = 10):
        self.client_pool: ConnectionPool = redis.ConnectionPool.from_url(url=url, max_connections=max_connections)

    def get(self, key: str) -> Any:
        redis_conn: StrictRedis = redis.StrictRedis(connection_pool=self.client_pool)
        redis_conn.ping()
        return redis_conn.get(key)

    def set(self, key: str, value: Any, expire: int = 0):
        redis_conn: StrictRedis = redis.StrictRedis(connection_pool=self.client_pool)
        redis_conn.ping()
        redis_conn.set(key, value)
        if expire > 0:
            redis_conn.expire(key, expire)

    def delete(self, key: str):
        redis_conn: StrictRedis = redis.StrictRedis(connection_pool=self.client_pool)
        redis_conn.ping()
        redis_conn.delete(key)

    def expire(self, key: str, expire: int):
        redis_conn: StrictRedis = redis.StrictRedis(connection_pool=self.client_pool)
        redis_conn.ping()
        redis_conn.expire(key, expire)
