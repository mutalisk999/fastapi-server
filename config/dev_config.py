#!/usr/bin/env python
# encoding: utf-8
from config.base_config import BaseConfig


class DevelopmentConfig(BaseConfig):
    class Config:
        env_file = ".env.dev"
        case_sensitive = True
