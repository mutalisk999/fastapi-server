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
    """Release the current thread's connection after a request.

    Must be called from the same thread that ran the queries, because peewee
    connections are thread-local. For playhouse pooled databases close()
    RETURNS the connection to the pool (it does not close the socket), so this
    must also run for pooled DBs - skipping it would leave the connection
    checked out of the pool forever.
    """
    try:
        if not database_proxy.is_closed():
            database_proxy.close()
    except Exception:
        pass


def shutdown_database():
    """Close every connection owned by the database at process shutdown.

    For playhouse pooled databases close_all() closes both idle and in-use
    connections; for a plain database it falls back to closing this thread's
    connection.
    """
    db_obj = getattr(database_proxy, "obj", None)
    if db_obj is None:
        return
    if hasattr(db_obj, "close_all"):  # playhouse PooledDatabase
        db_obj.close_all()
    elif not db_obj.is_closed():
        db_obj.close()


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
        try:
            with database_proxy.atomic():
                result = await func(*args, **kwargs)
            return result
        finally:
            # Must run even when the endpoint raises, or the connection is
            # never returned to the pool / closed.
            _close_request_connection()

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            with database_proxy.atomic():
                result = func(*args, **kwargs)
            return result
        finally:
            _close_request_connection()

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
