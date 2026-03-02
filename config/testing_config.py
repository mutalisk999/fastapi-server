#!/usr/bin/env python
# encoding: utf-8
from config.base_config import BaseConfig


class TestingConfig(BaseConfig):
    class Config:
        env_file = ".env.testing"
        case_sensitive = True
