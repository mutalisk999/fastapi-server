#!/usr/bin/env python
# encoding: utf-8
from pydantic_settings import BaseSettings
from typing import Optional, List


class BaseConfig(BaseSettings):
    # JWT configuration
    JWT_SECRET: Optional[str] = None

    # Database configuration
    DATABASE_USER: Optional[str] = None
    DATABASE_PASS: Optional[str] = None
    DATABASE_HOST: Optional[str] = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_NAME: Optional[str] = None
    DATABASE_CHARSET: Optional[str] = "utf8mb4"
    DATABASE_POOL_SIZE: int = 5

    # Redis configuration
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # CORS configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Server configuration
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 7788

    # Logger configuration
    LOG_FILE_NAME: Optional[str] = "app.log"
    LOG_LEVEL: Optional[str] = "INFO"
    LOG_FILE_SIZE: int = 10*1024*1024
    LOG_BACKUP_COUNT: int = 5
    
    class Config:
        case_sensitive = True
