#!/usr/bin/env python
# encoding: utf-8
import os

from dotenv import load_dotenv

from config.base_config import BaseConfig


class DevelopmentConfig(BaseConfig):
    @staticmethod
    def initialize(env_file: str = ".env.dev"):
        load_dotenv(dotenv_path=env_file)

        DevelopmentConfig.JWT_SECRET = os.environ.get("JWT_SECRET")

        DevelopmentConfig.DATABASE_USER = os.environ.get("DATABASE_USER")
        DevelopmentConfig.DATABASE_PASS = os.environ.get("DATABASE_PASS")
        DevelopmentConfig.DATABASE_HOST = os.environ.get("DATABASE_HOST")
        DevelopmentConfig.DATABASE_PORT = int(os.environ.get("DATABASE_PORT", 3306))
        DevelopmentConfig.DATABASE_NAME = os.environ.get("DATABASE_NAME")
        DevelopmentConfig.DATABASE_CHARSET = os.environ.get("DATABASE_CHARSET")

        DevelopmentConfig.REDIS_URL = os.environ.get("REDIS_URL")
