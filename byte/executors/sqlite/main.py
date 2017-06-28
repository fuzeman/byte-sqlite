"""byte-sqlite - executor module."""
from __future__ import absolute_import, division, print_function

from byte.core.plugin.base import Plugin
from byte.executors.core.base import DatabaseExecutorPlugin
from byte.executors.sqlite.models.connection import SqliteConnection
from byte.executors.sqlite.models.cursor import SqliteCursor
from byte.executors.sqlite.models.transaction import SqliteTransaction
from byte.executors.sqlite.tasks import SqliteInsertTask, SqliteSelectTask
from byte.queries import InsertQuery, SelectQuery

import logging
import os
import sqlite3

log = logging.getLogger(__name__)


class Base(DatabaseExecutorPlugin):
    """SQLite base executor class."""

    class Meta(DatabaseExecutorPlugin.Meta):
        """SQLite base executor metadata."""

        content_type = 'application/x-sqlite3'

        extension = [
            'db',
            'sqlite'
        ]

        scheme = [
            'sqlite'
        ]

    @property
    def path(self):
        """Retrieve database path.

        :return: Database Path
        :rtype: str
        """
        path = (
            self.uri.netloc +
            self.uri.path
        )

        if path == ':memory:':
            return path

        return os.path.abspath(path)

    def construct_compiler(self):
        """Construct compiler."""
        # Find matching compiler
        cls = self.plugins.match(
            Plugin.Kind.Compiler,
            engine=Plugin.Engine.Table,
            extension='sqlite'
        )

        if not cls:
            return None

        # Construct compiler
        self._compiler = cls(self, version=sqlite3.sqlite_version_info)
        return self._compiler

    def create_connection(self):
        """Connect to database.

        :return: SQLite Connection
        :rtype: sqlite3.Connection
        """
        # Connect to database
        instance = sqlite3.connect(self.path)
        instance.isolation_level = None

        # Create connection
        connection = SqliteConnection(self, instance)

        # Configure connection
        with connection.transaction() as transaction:
            # Enable write-ahead logging
            transaction.execute('PRAGMA journal_mode=WAL;')

        return connection

    def create_transaction(self, connection=None):
        """Create database transaction.

        :return: SQLite Connection
        :rtype: sqlite3.Connection
        """
        return SqliteTransaction(
            self,
            connection=connection
        )

    def cursor(self, connection=None):
        """Create database cursor.

        :return: Cursor
        :rtype: byte.executors.sqlite.models.cursor.SqliteCursor
        """
        return SqliteCursor(
            self,
            connection=connection
        )

    def execute(self, query):
        """Execute query.

        :param query: Query
        :type query: byte.queries.Query
        """
        statements = self.compiler.compile(query)

        if not statements:
            raise ValueError('No statements returned from compiler')

        # Construct task
        if isinstance(query, SelectQuery):
            return SqliteSelectTask(self, statements).execute()

        if isinstance(query, InsertQuery):
            return SqliteInsertTask(self, statements).execute()

        raise NotImplementedError('Unsupported query: %s' % (type(query).__name__,))


class SqliteDatabaseExecutor(Base):
    """SQLite database executor class."""

    key = 'database'

    class Meta(Base.Meta):
        """SQLite database executor metadata."""

        engine = Plugin.Engine.Database

    def open_table(self, table):
        """Open SQLite table executor for :code:`table`.

        :param table: Table
        :type table: byte.engines.table.Table

        :return: Table Executor
        :rtype: SqliteTableExecutor
        """
        return SqliteTableExecutor(
            table, self.uri,
            connections=self.connections,
            transactions=self.transactions,
            **self.parameters
        )


class SqliteTableExecutor(Base):
    """SQLite table executor class."""

    key = 'table'

    class Meta(Base.Meta):
        """SQLite table executor metadata."""

        engine = Plugin.Engine.Table
