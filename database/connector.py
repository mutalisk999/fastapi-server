#!/usr/bin/env python
# encoding: utf-8

from peewee import InterfaceError, SENTINEL  # type: ignore
from peewee import SqliteDatabase, MySQLDatabase, PostgresqlDatabase
from playhouse.shortcuts import ReconnectMixin  # type: ignore
from playhouse.pool import (
    PooledSqliteDatabase,
    PooledMySQLDatabase,
    PooledPostgresqlDatabase,
)


class ReconnectMixinNew(ReconnectMixin):
    def execute_sql(self, sql, params=None, commit=SENTINEL):
        try:
            return super(ReconnectMixin, self).execute_sql(sql, params, commit)
        except Exception as exc:
            exc_class = type(exc)
            if (
                exc_class not in self._reconnect_errors
                and exc_class is not InterfaceError
            ):
                raise exc

            if exc_class in self._reconnect_errors:
                exc_repr = str(exc).lower()
                for err_fragment in self._reconnect_errors[exc_class]:
                    if err_fragment in exc_repr:
                        break
                else:
                    raise exc

            if not self.is_closed():
                self.close()
                self.connect()

            return super(ReconnectMixin, self).execute_sql(sql, params, commit)


class ReconnectSqliteDatabase(ReconnectMixinNew, SqliteDatabase):
    pass


class ReconnectPooledSqliteDatabase(ReconnectMixinNew, PooledSqliteDatabase):
    pass


class ReconnectMySQLDatabase(ReconnectMixinNew, MySQLDatabase):
    pass


class ReconnectPooledMySQLDatabase(ReconnectMixinNew, PooledMySQLDatabase):
    pass


class ReconnectPostgresqlDatabase(ReconnectMixinNew, PostgresqlDatabase):
    pass


class ReconnectPooledPostgresqlDatabase(ReconnectMixinNew, PooledPostgresqlDatabase):
    pass
