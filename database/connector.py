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

            # Check if this exception type is a reconnectable error
            is_reconnectable = False
            if exc_class in self._reconnect_errors:
                # Check if the error message matches any known fragment
                exc_repr = str(exc).lower()
                for err_fragment in self._reconnect_errors[exc_class]:
                    if err_fragment in exc_repr:
                        is_reconnectable = True
                        break
            elif exc_class is InterfaceError:
                # InterfaceError is always reconnectable
                is_reconnectable = True

            if not is_reconnectable:
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
