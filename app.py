#!/usr/bin/env python
# encoding: utf-8
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from config import DevelopmentConfig, ProductionConfig, TestingConfig, configs
from typing import Union, Dict

from controller import mock_router
from controller.user_controller import user_router
from controller.auth_controller import auth_router
from database import database_proxy
from database.connector import ReconnectMySQLDatabase, ReconnectPooledMySQLDatabase
from utils.authentication import auth_handler
from utils.crypto_tools import Aes128Cbc
from utils.logger import init_logger, logger

from utils.redis_client import RedisClient


async def db_session_middleware(request: Request, call_next):
    """Middleware to handle database transactions for each request."""
    try:
        # Process the request
        response = await call_next(request)
        # Commit successful transactions if any
        try:
            if not database_proxy.is_closed():
                database_proxy.commit()
        except Exception:
            pass
        return response
    except Exception:
        # Rollback on exception
        try:
            if not database_proxy.is_closed():
                database_proxy.rollback()
        except Exception:
            pass
        raise


async def error_handler_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


class Application(object):
    setting: Union[DevelopmentConfig, TestingConfig, ProductionConfig, None] = None
    config_pass: str = ""
    global_stop: bool = False
    redis_client: Union[RedisClient, None] = None

    @staticmethod
    def create_app(config_name: str, config_pass: str):
        setting = configs[config_name]()
        Application.setting = setting
        Application.config_pass = config_pass
        Application.redis_client = RedisClient(
            url=setting.REDIS_URL, max_connections=10
        )

        aes128 = Aes128Cbc(Application.config_pass.encode("ascii"))
        database_pass = aes128.aes128_cbc_decrypt(setting.DATABASE_PASS)

        jwt_secret = aes128.aes128_cbc_decrypt(setting.JWT_SECRET)
        auth_handler.initialize(jwt_secret)

        if setting.DATABASE_POOL_SIZE <= 1:
            db = ReconnectMySQLDatabase(
                setting.DATABASE_NAME,
                autocommit=False,
                autorollback=False,
                **{
                    "host": setting.DATABASE_HOST,
                    "port": setting.DATABASE_PORT,
                    "user": setting.DATABASE_USER,
                    "password": database_pass,
                    "use_unicode": True,
                    "charset": setting.DATABASE_CHARSET,
                },
            )
            database_proxy.initialize(db)
        else:
            db_pool = ReconnectPooledMySQLDatabase(
                setting.DATABASE_NAME,
                max_connections=setting.DATABASE_POOL_SIZE,
                stale_timeout=300,
                autocommit=False,
                autorollback=False,
                **{
                    "host": setting.DATABASE_HOST,
                    "port": setting.DATABASE_PORT,
                    "user": setting.DATABASE_USER,
                    "password": database_pass,
                    "use_unicode": True,
                    "charset": setting.DATABASE_CHARSET,
                },
            )
            database_proxy.initialize(db_pool)

        app = FastAPI()
        api_router = APIRouter()
        api_router.include_router(prefix="/mock", router=mock_router, tags=["mock"])
        api_router.include_router(prefix="/users", router=user_router, tags=["users"])
        api_router.include_router(prefix="/auth", router=auth_router, tags=["auth"])
        app.include_router(prefix="/api", router=api_router)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=setting.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )
        app.middleware("http")(error_handler_middleware)
        app.middleware("http")(db_session_middleware)

        # Reinitialize logger with config parameters
        init_logger()
        logger.info(
            f"Logger initialized with config: file={Application.setting.LOG_FILE_NAME}, level={Application.setting.LOG_LEVEL}"
        )

        return app
