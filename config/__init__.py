#!/usr/bin/env python
# encoding: utf-8


from config.dev_config import DevelopmentConfig
from config.testing_config import TestingConfig
from config.prod_config import ProductionConfig

configs = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
