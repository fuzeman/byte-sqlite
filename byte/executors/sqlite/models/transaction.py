"""byte-sqlite - executor transaction module."""
from __future__ import absolute_import, division, print_function

from byte.executors.core.models.database import DatabaseTransaction
from byte.executors.sqlite.models.cursor import SqliteCursor

import logging

log = logging.getLogger(__name__)


class SqliteTransaction(DatabaseTransaction, SqliteCursor):
    """SQLite transaction class."""

    def begin(self):
        """Begin transaction."""
        self.instance.execute('BEGIN;')

        log.debug('BEGIN')

    def commit(self):
        """Commit transaction."""
        log.debug('COMMIT')

        self.connection.instance.commit()

    def rollback(self):
        """Rollback transaction."""
        log.debug('ROLLBACK')

        self.connection.instance.rollback()

    def close(self):
        log.debug('CLOSE')

        # Close cursor
        self.instance.close()
        self.instance = None

        # Close transaction
        super(SqliteTransaction, self).close()
