#!/usr/bin/env python
# encoding: utf-8
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import DevelopmentConfig, ProductionConfig, TestingConfig, configs
from typing import Union

from controller import mock_router
from controller.user_controller import user_router
from controller.auth_controller import auth_router
from database import database_proxy, shutdown_database
from database.connector import ReconnectMySQLDatabase, ReconnectPooledMySQLDatabase
from thread_task import thread_manager
from utils.authentication import auth_handler
from utils.crypto_tools import AesGcm
from utils.logger import init_logger, logger

from utils.redis_client import RedisClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Graceful shutdown: tell background threads to stop and wait for them.
    # Runs via uvicorn's lifespan when the server stops (Ctrl+C / SIGTERM).
    Application.global_stop = True
    try:
        await asyncio.to_thread(thread_manager.stop_all_threads)
    except Exception as e:
        logger.error(f"Error stopping threads during shutdown: {e}")
    # Drain the database connection pool (closes idle and in-use connections).
    # Wrapped in to_thread because closing sockets is blocking network I/O.
    try:
        await asyncio.to_thread(shutdown_database)
    except Exception as e:
        logger.error(f"Error closing database connections during shutdown: {e}")
    # Disconnect all pooled Redis connections.
    if Application.redis_client is not None:
        try:
            await asyncio.to_thread(Application.redis_client.client_pool.disconnect)
        except Exception as e:
            logger.error(f"Error closing Redis connections during shutdown: {e}")


async def db_session_middleware(request: Request, call_next):
    """Middleware to handle database transactions for each request.

    NOTE: peewee connections are thread-local. This async middleware runs on the
    event-loop thread, so its commit/rollback only affects async endpoints
    (which share that thread). For sync endpoints FastAPI runs in a threadpool
    worker thread, so use the @db_transaction decorator (database.db_transaction)
    instead of relying on this middleware.
    """
    try:
        response = await call_next(request)
        # Commit successful transactions if any
        try:
            if not database_proxy.is_closed():
                database_proxy.commit()
        except Exception as e:
            logger.error(
                f"Database commit failed for {request.method} {request.url.path} "
                f"({type(e).__name__}: {e})"
            )
        return response
    except Exception:
        # Rollback on exception
        try:
            if not database_proxy.is_closed():
                database_proxy.rollback()
        except Exception as e:
            logger.error(
                f"Database rollback failed for {request.method} {request.url.path} "
                f"({type(e).__name__}: {e})"
            )
        raise
    finally:
        try:
            if not database_proxy.is_closed():
                # For pooled databases close() returns the connection to the
                # pool instead of closing it, so this is safe (and required)
                # for both pooled and non-pooled databases.
                database_proxy.close()
        except Exception as e:
            logger.error(
                f"Failed to release database connection for "
                f"{request.method} {request.url.path} ({type(e).__name__}: {e})"
            )


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

        aes_gcm = AesGcm(Application.config_pass.encode("utf-8"))

        # Validate required secrets before decrypting, so a missing or non-hex
        # value fails startup with a clear message instead of a cryptic error.
        if not setting.DATABASE_PASS:
            raise ValueError("DATABASE_PASS is not set in the environment")
        if not setting.JWT_SECRET:
            raise ValueError("JWT_SECRET is not set in the environment")
        try:
            database_pass = aes_gcm.decrypt(setting.DATABASE_PASS)
        except Exception as e:
            # Includes ValueError (bad hex) and cryptography InvalidTag (wrong
            # config password) - fail startup with a clear, actionable message.
            raise ValueError(
                "Cannot decrypt DATABASE_PASS - check the config password and "
                f"that the env value is AES-256-GCM encrypted hex. ({type(e).__name__}: {e})"
            )
        try:
            jwt_secret = aes_gcm.decrypt(setting.JWT_SECRET)
        except Exception as e:
            raise ValueError(
                "Cannot decrypt JWT_SECRET - check the config password and "
                f"that the env value is AES-256-GCM encrypted hex. ({type(e).__name__}: {e})"
            )
        auth_handler.initialize(jwt_secret)
        if len(jwt_secret.encode("utf-8")) < 32:
            logger.warning(
                "JWT_SECRET is shorter than 32 bytes - HMAC-SHA256 keys should be at least 32 bytes."
            )

        if setting.DATABASE_POOL_SIZE <= 1:
            db = ReconnectMySQLDatabase(
                setting.DATABASE_NAME,
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

        app = FastAPI(lifespan=lifespan)
        api_router = APIRouter()
        api_router.include_router(prefix="/mock", router=mock_router, tags=["mock"])
        api_router.include_router(prefix="/users", router=user_router, tags=["users"])
        api_router.include_router(prefix="/auth", router=auth_router, tags=["auth"])
        app.include_router(prefix="/api", router=api_router)
        # Middleware order (outer → inner): CORS → error_handler → db_session.
        # Starlette's add_middleware inserts at index 0, so the LAST registered
        # middleware is the OUTERMOST. Registering db_session first makes it the
        # innermost, so a route exception first rolls back the DB transaction in
        # db_session, then is converted to a JSON error response by error_handler,
        # and finally gets CORS headers from the outermost CORS middleware.
        app.middleware("http")(db_session_middleware)
        app.middleware("http")(error_handler_middleware)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=setting.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )

        # Reinitialize logger with config parameters
        init_logger()
        logger.info(
            f"Logger initialized with config: file={Application.setting.LOG_FILE_NAME}, level={Application.setting.LOG_LEVEL}"
        )

        return app
