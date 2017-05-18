"""byte-sqlite - executor module."""
from __future__ import absolute_import, division, print_function

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


class SqliteExecutor(DatabaseExecutorPlugin):
    """SQLite executor class."""

    key = 'sqlite'

    class Meta(DatabaseExecutorPlugin.Meta):
        """SQLite executor metadata."""

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
            self.collection.uri.netloc +
            self.collection.uri.path
        )

        if path == ':memory:':
            return path

        return os.path.abspath(path)

    def construct_compiler(self):
        """Construct compiler."""
        return self.plugins.get_compiler('sqlite')(
            self,
            version=sqlite3.sqlite_version_info
        )

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
