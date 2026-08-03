#!/usr/bin/env python
# encoding: utf-8
from config.base_config import BaseConfig


class DevelopmentConfig(BaseConfig):
    model_config = {"case_sensitive": True, "env_file": ".env.dev"}
