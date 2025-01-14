#!/usr/bin/env python
# encoding: utf-8
import os

from dotenv import load_dotenv

from config.base_config import BaseConfig


class ProductionConfig(BaseConfig):
    @staticmethod
    def initialize(env_file: str = ".env.prod"):
        load_dotenv(dotenv_path=env_file)

        ProductionConfig.JWT_SECRET = os.environ.get("JWT_SECRET")

        ProductionConfig.DATABASE_USER = os.environ.get("DATABASE_USER")
        ProductionConfig.DATABASE_PASS = os.environ.get("DATABASE_PASS")
        ProductionConfig.DATABASE_HOST = os.environ.get("DATABASE_HOST")
        ProductionConfig.DATABASE_PORT = int(os.environ.get("DATABASE_PORT", 3306))
        ProductionConfig.DATABASE_NAME = os.environ.get("DATABASE_NAME")
        ProductionConfig.DATABASE_CHARSET = os.environ.get("DATABASE_CHARSET")
        ProductionConfig.DATABASE_POOL_SIZE = int(os.environ.get("DATABASE_POOL_SIZE", 20))

        ProductionConfig.REDIS_URL = os.environ.get("REDIS_URL")
