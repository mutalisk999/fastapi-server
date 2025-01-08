#!/usr/bin/env python
# encoding: utf-8
from typing import Optional


class BaseConfig(object):
    JWT_SECRET: Optional[str]

    DATABASE_USER: Optional[str]
    DATABASE_PASS: Optional[str]
    DATABASE_HOST: Optional[str]
    DATABASE_PORT: int
    DATABASE_NAME: Optional[str]
    DATABASE_CHARSET: Optional[str]

    REDIS_URL: Optional[str]
