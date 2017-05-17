"""byte-sqlite - executor transaction module."""
from __future__ import absolute_import, division, print_function

from byte.executors.core.models.database import DatabaseTransaction
from byte.executors.sqlite.models.cursor import SqliteCursor


class SqliteTransaction(DatabaseTransaction, SqliteCursor):
    """SQLite transaction class."""

    def begin(self):
        """Begin transaction."""
        self.instance.execute('BEGIN;')

    def commit(self):
        """Commit transaction."""
        self.connection.instance.commit()

    def rollback(self):
        """Rollback transaction."""
        self.connection.instance.rollback()
