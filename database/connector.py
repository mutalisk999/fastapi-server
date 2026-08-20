#!/usr/bin/env python
# encoding: utf-8 -*-

import time

from peewee import InterfaceError, SENTINEL  # type: ignore
from peewee import SqliteDatabase, MySQLDatabase, PostgresqlDatabase
from playhouse.shortcuts import ReconnectMixin  # type: ignore
from playhouse.pool import (
    PooledSqliteDatabase,
    PooledMySQLDatabase,
    PooledPostgresqlDatabase,
)

# How long a thread waits for a free pooled connection before failing.
# playhouse pools do NOT queue: without this, a burst of concurrent requests
# exceeding max_connections fails immediately with "Exceeded maximum
# connections". Since connections are returned per-request, the wait is
# normally short.
POOL_ACQUIRE_TIMEOUT = 3.0
_ACQUIRE_POLL_INTERVAL = 0.05


class ReconnectMixinNew(ReconnectMixin):
    def execute_sql(self, sql, params=None, commit=SENTINEL):
        try:
            return super(ReconnectMixin, self).execute_sql(sql, params, commit)
        except Exception as exc:
            # Never reconnect mid-transaction: closing the connection would drop
            # any pending changes, and re-executing the statement outside the
            # transaction could commit partial state or duplicate writes.
            if self.in_transaction():
                raise exc

            exc_class = type(exc)

            # Check if this exception type is a reconnectable error
            is_reconnectable = False
            if exc_class in self._reconnect_errors:
                # Check if the error message matches any known fragment
                exc_repr = str(exc).lower()
                for err_fragment in self._reconnect_errors[exc_class]:
                    if err_fragment in exc_repr:
                        is_reconnectable = True
                        break
            elif isinstance(exc, InterfaceError):
                # InterfaceError is always reconnectable
                is_reconnectable = True

            if not is_reconnectable:
                raise exc

            if not self.is_closed():
                self.close()
                self.connect()

            return super(ReconnectMixin, self).execute_sql(sql, params, commit)


class BlockingPoolMixin(object):
    """Make a playhouse pool wait briefly for a free connection instead of
    raising "Exceeded maximum connections" on short concurrency bursts.

    The retry loop lives in connect(), NOT _connect(): peewee calls _connect()
    while holding Database._lock, so sleeping there would block other threads
    from returning their connections (close() needs the same lock) and every
    waiter would time out. Retrying in connect() keeps each attempt short and
    sleeps with the lock released.
    """

    def connect(self, reuse_if_open=False):
        deadline = time.monotonic() + POOL_ACQUIRE_TIMEOUT
        while True:
            try:
                return super().connect(reuse_if_open)
            except ValueError as exc:
                if "Exceeded maximum connections" not in str(exc):
                    raise
                if time.monotonic() >= deadline:
                    raise
                time.sleep(_ACQUIRE_POLL_INTERVAL)


class ReconnectSqliteDatabase(ReconnectMixinNew, SqliteDatabase):
    pass


class ReconnectPooledSqliteDatabase(
    BlockingPoolMixin, ReconnectMixinNew, PooledSqliteDatabase
):
    pass


class ReconnectMySQLDatabase(ReconnectMixinNew, MySQLDatabase):
    pass


class ReconnectPooledMySQLDatabase(
    BlockingPoolMixin, ReconnectMixinNew, PooledMySQLDatabase
):
    pass


class ReconnectPostgresqlDatabase(ReconnectMixinNew, PostgresqlDatabase):
    pass


class ReconnectPooledPostgresqlDatabase(
    BlockingPoolMixin, ReconnectMixinNew, PooledPostgresqlDatabase
):
    pass
