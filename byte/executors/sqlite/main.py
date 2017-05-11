"""byte-sqlite - executor module."""
from __future__ import absolute_import, division, print_function

from byte.executors.sqlite.tasks import SqliteSelectTask
from byte.executors.core.base import ExecutorPlugin
from byte.statements import SelectStatement

import os
import sqlite3


class SqliteExecutor(ExecutorPlugin):
    """SQLite executor class."""

    key = 'sqlite'

    class Meta(ExecutorPlugin.Meta):
        """SQLite executor metadata."""

        content_type = 'application/x-sqlite3'

        extension = [
            'db',
            'sqlite'
        ]

        scheme = [
            'sqlite'
        ]

    def __init__(self, collection, model):
        """Create SQLite executor.

        :param collection: Collection
        :type collection: byte.collection.Collection

        :param model: Model
        :type model: byte.model.Model
        """
        super(SqliteExecutor, self).__init__(collection, model)

        self.connection = None

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
        return self.plugins.get_compiler('sqlite')(self)

    def connect(self):
        """Connect to database.

        :return: SQLite Connection
        :rtype: sqlite3.Connection
        """
        if self.connection:
            return self.connection

        # Connect to database
        self.connection = sqlite3.connect(self.path)

        # Enable write-ahead logging
        self.connection.cursor().execute('PRAGMA journal_mode=WAL;')

        return self.connection

    def cursor(self):
        """Create database cursor.

        :return: SQLite Cursor
        :rtype: sqlite3.Cursor
        """
        return self.connect().cursor()

    def execute(self, statement):
        """Execute statement.

        :param statement: Statement
        :type statement: byte.statements.core.base.Statement
        """
        sql, parameters = self.compiler.compile(statement)

        if not sql:
            raise ValueError('Empty statement')

        # Construct task
        if isinstance(statement, SelectStatement):
            return SqliteSelectTask(self, sql, parameters).execute()

        raise NotImplementedError('Unsupported statement: %s' % (type(statement).__name__,))
