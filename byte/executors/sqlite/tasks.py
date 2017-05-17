"""byte-sqlite - executor tasks module."""
from __future__ import absolute_import, division, print_function

from contextlib import closing

from byte.core.models import Task, ReadTask, SelectTask, WriteTask

import logging
import sys

log = logging.getLogger(__name__)


class SqliteTask(Task):
    """SQLite task base class."""

    def __init__(self, executor, statements):
        """Create SQLite executor task.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor

        :param statements: SQLite Statements
        :type statements: list of (str, tuple)
        """
        super(SqliteTask, self).__init__(executor)

        self.statements = statements


class SqliteReadTask(ReadTask, SqliteTask):
    """SQLite read task class."""

    def __init__(self, executor, statements):
        super(SqliteReadTask, self).__init__(executor, statements)

        self.cursor = self.executor.cursor()

    def execute(self):
        """Execute task."""
        for operation in self.statements:
            if not isinstance(operation, tuple) or len(operation) != 2:
                raise ValueError('Invalid statement returned from compiler: %s' % (operation,))

            log.debug('Execute: %r %r', *operation)
            self.cursor.execute(*operation)

        return self

    def close(self):
        """Close task."""
        self.cursor.close()


class SqliteSelectTask(SelectTask, SqliteReadTask):
    """SQLite select task class."""

    def items(self):
        """Retrieve items from task."""
        # Parse items from cursor
        for row in self.cursor:
            yield self.model.from_plain(
                self._build_item(row),
                translate=True
            )

        # Close cursor
        self.close()

    def _build_item(self, row):
        data = {}

        for i, column in enumerate(self.cursor.columns):
            data[column[0]] = row[i]

        return data


class SqliteWriteTask(WriteTask, SqliteTask):
    """SQLite write task class."""

    def __init__(self, executor, statements):
        super(SqliteWriteTask, self).__init__(executor, statements)

        self.transaction_created, self.transaction = self.executor.transaction(state=True)

    def execute(self):
        """Execute task."""
        with self.transaction:
            for operation in self.statements:
                if not isinstance(operation, tuple) or len(operation) != 2:
                    raise ValueError('Invalid statement returned from compiler: %s' % (operation,))

                log.debug('Execute: %r %r', *operation)
                self.transaction.execute(*operation)

        return self

    def close(self):
        """Close task."""
        if not self.transaction_created:
            return

        self.transaction.close()


class SqliteInsertTask(SqliteWriteTask):
    """SQLite insert task class."""

    pass
