from byte.executors.core.models.database import DatabaseTransaction
from byte.executors.sqlite.models.cursor import SqliteCursor

import logging

log = logging.getLogger(__name__)


class SqliteTransaction(DatabaseTransaction, SqliteCursor):
    def begin(self):
        if self.state >= DatabaseTransaction.State.Done:
            raise Exception('Transaction has already been used')

        if self.state >= DatabaseTransaction.State.Started:
            raise Exception('Transaction has already been started')

        # Update state
        self.state = DatabaseTransaction.State.Started

        # Begin transaction
        self.instance.execute('BEGIN;')

        log.debug('BEGIN')

    def commit(self):
        if self.state >= DatabaseTransaction.State.Done:
            raise Exception('Transaction has already finished')

        log.debug('COMMIT')

        # Commit transaction
        self.connection.commit()

        # Update state
        self.state = DatabaseTransaction.State.Done

    def rollback(self):
        if self.state >= DatabaseTransaction.State.Done:
            raise Exception('Transaction has already finished')

        log.debug('ROLLBACK')

        # Rollback transaction
        self.connection.rollback()

        # Update state
        self.state = DatabaseTransaction.State.Done
