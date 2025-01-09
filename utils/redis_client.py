#!/usr/bin/env python
# encoding: utf-8
from typing import Any

import redis
from redis.client import Redis


class RedisClient(object):
    def __init__(self, url: str = "redis://127.0.0.1:6379"):
        self.client: Redis = redis.from_url(url=url)
        self.client.ping()

    def get(self, key: str) -> Any:
        self.client.ping()
        return self.client.get(key)

    def set(self, key: str, value: Any, expire: int = 0):
        self.client.ping()
        self.client.set(key, value)
        if expire > 0:
            self.client.expire(key, expire)

    def delete(self, key: str):
        self.client.ping()
        self.client.delete(key)

    def expire(self, key: str, expire: int):
        self.client.ping()
        self.client.expire(key, expire)

    def ping(self):
        return self.client.ping()
