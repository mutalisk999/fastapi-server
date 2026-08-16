#!/usr/bin/env python
# encoding: utf-8

import asyncio
from functools import wraps

from peewee import *

database_proxy = DatabaseProxy()


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database_proxy


def _close_request_connection():
    """Close the current thread's connection after a request for non-pooled DBs.

    Must be called from the same thread that ran the queries, because peewee
    connections are thread-local.
    """
    try:
        if not database_proxy.is_closed():
            db_obj = database_proxy.obj
            if db_obj and not hasattr(db_obj, "max_connections"):
                database_proxy.close()
    except Exception:
        pass


def db_transaction(func):
    """Wrap an endpoint so all DB work runs inside one atomic transaction.

    The transaction and connection cleanup run in the SAME thread as the
    endpoint function. This matters because peewee connections are thread-local
    and FastAPI runs sync endpoints in a threadpool: an async middleware would
    commit/rollback the event-loop thread's connection, not the one the endpoint
    actually used.

    Apply this decorator to endpoints that touch the database (instead of
    relying on db_session_middleware, which only works for async endpoints).
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        with database_proxy.atomic():
            result = await func(*args, **kwargs)
        _close_request_connection()
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        with database_proxy.atomic():
            result = func(*args, **kwargs)
        _close_request_connection()
        return result

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
