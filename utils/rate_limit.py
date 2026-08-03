#!/usr/bin/env python
# encoding: utf-8
import time
from functools import wraps
from fastapi import HTTPException, Request
from utils.logger import logger


def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    """Rate limit decorator using Redis. Falls back to in-memory if Redis unavailable.

    The decorated function must accept `request: Request` as a parameter
    for FastAPI to inject the Request object.
    """
    _memory_store: dict = {}

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract Request from FastAPI-injected parameters
            request = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            if request is None:
                return await func(*args, **kwargs)

            client_ip = request.client.host if request.client else "unknown"
            key = f"rate_limit:{func.__name__}:{client_ip}"

            # Try Redis first
            try:
                from app import Application
                redis_client = Application.redis_client
                if redis_client:
                    current = redis_client.get(key)
                    if current is None:
                        redis_client.set(key, "1", expire=window_seconds)
                    else:
                        count = int(current)
                        if count >= max_requests:
                            logger.warning(f"Rate limit exceeded for {client_ip} on {func.__name__}")
                            raise HTTPException(
                                status_code=429,
                                detail="Too many requests. Please try again later."
                            )
                        redis_client.redis_client.incr(key)
                    return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception:
                pass

            # Fallback to in-memory rate limiting
            now = time.time()
            if key not in _memory_store:
                _memory_store[key] = []

            _memory_store[key] = [t for t in _memory_store[key] if now - t < window_seconds]

            if len(_memory_store[key]) >= max_requests:
                logger.warning(f"Rate limit exceeded for {client_ip} on {func.__name__}")
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )

            _memory_store[key].append(now)
            return await func(*args, **kwargs)

        return wrapper
    return decorator
