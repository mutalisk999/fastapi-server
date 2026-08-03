#!/usr/bin/env python
# encoding: utf-8
from config.base_config import BaseConfig


class ProductionConfig(BaseConfig):
    DATABASE_POOL_SIZE: int = 20
    model_config = {"case_sensitive": True, "env_file": ".env.prod"}
