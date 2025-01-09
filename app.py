#!/usr/bin/env python
# encoding: utf-8
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from config import DevelopmentConfig, ProductionConfig, TestingConfig, configs
from typing import Union, Dict

from controller import mock_router
from database import database_proxy
from database.connector import ReconnectMySQLDatabase
from utils.authentication import AuthHandler
from utils.crypto_tools import Aes128Ctr

from utils.redis_client import RedisClient


class Application(object):
    setting: Union[DevelopmentConfig, TestingConfig, ProductionConfig, None] = None
    config_pass: str = ""
    global_stop: bool = False
    redis_client: Union[RedisClient, None] = None
    thread_running_dict: Dict = {}

    @staticmethod
    def create_app(config_name: str, config_pass: str):
        setting = configs[config_name]
        setting.initialize()
        Application.setting = setting
        Application.config_pass = config_pass
        Application.redis_client = RedisClient(url=setting.REDIS_URL)
        r = Application.redis_client.ping()
        print(r)

        aes128 = Aes128Ctr(Application.config_pass.encode("ascii"))
        database_pass = aes128.aes128_ctr_decrypt(setting.DATABASE_PASS)

        jwt_secret = aes128.aes128_ctr_decrypt(setting.JWT_SECRET)
        AuthHandler.initialize(jwt_secret)

        db = ReconnectMySQLDatabase(
            setting.DATABASE_NAME, autocommit=False, autorollback=False,
            **{'host': setting.DATABASE_HOST, 'port': setting.DATABASE_PORT,
               'user': setting.DATABASE_USER,
               'password': database_pass,
               'use_unicode': True,
               'charset': setting.DATABASE_CHARSET})

        database_proxy.initialize(db)

        app = FastAPI()
        api_router = APIRouter()
        api_router.include_router(prefix="/mock", router=mock_router, tags=['mock'])
        app.include_router(prefix="/api", router=api_router)
        app.add_middleware(CORSMiddleware, allow_origins=["*"],
                           allow_credentials=True, allow_methods=["*"],
                           allow_headers=["*"],
                           )
        return app
