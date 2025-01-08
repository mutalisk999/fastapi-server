#!/usr/bin/env python
# encoding: utf-8
import os

from dotenv import load_dotenv

from config.base_config import BaseConfig


class TestingConfig(BaseConfig):
    @staticmethod
    def initialize(env_file: str = ".env.testing"):
        load_dotenv(dotenv_path=env_file)

        TestingConfig.JWT_SECRET = os.environ.get("JWT_SECRET")

        TestingConfig.DATABASE_USER = os.environ.get("DATABASE_USER")
        TestingConfig.DATABASE_PASS = os.environ.get("DATABASE_PASS")
        TestingConfig.DATABASE_HOST = os.environ.get("DATABASE_HOST")
        TestingConfig.DATABASE_PORT = int(os.environ.get("DATABASE_PORT", 3306))
        TestingConfig.DATABASE_NAME = os.environ.get("DATABASE_NAME")
        TestingConfig.DATABASE_CHARSET = os.environ.get("DATABASE_CHARSET")
