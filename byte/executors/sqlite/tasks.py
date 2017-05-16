"""byte-sqlite - executor tasks module."""
from __future__ import absolute_import, division, print_function

from byte.core.models import Task, ReadTask, SelectTask, WriteTask


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

        self.cursor = None

    def open(self):
        """Open task."""
        self.cursor = self.executor.cursor()

    def execute(self):
        """Execute task."""
        self.open()

        # Execute statements inside transaction
        with self.executor.transaction():
            for operation in self.statements:
                if not isinstance(operation, tuple) or len(operation) != 2:
                    raise ValueError('Invalid statement returned from compiler: %s' % (operation,))

                print('EXECUTE: %r %r' % operation)
                self.cursor.execute(*operation)

        return self

    def close(self):
        """Close task."""
        self.cursor.close()


class SqliteReadTask(ReadTask, SqliteTask):
    """SQLite read task class."""

    pass


class SqliteSelectTask(SelectTask, SqliteReadTask):
    """SQLite select task class."""

    def items(self):
        """Retrieve items from task."""
        for row in self.cursor:
            yield self.model.from_plain(
                self._build_item(row),
                translate=True
            )

    def _build_item(self, row):
        data = {}

        for i, column in enumerate(self.cursor.description):
            data[column[0]] = row[i]

        return data


class SqliteWriteTask(WriteTask, SqliteTask):
    """SQLite write task class."""

    pass


class SqliteInsertTask(SqliteWriteTask):
    """SQLite insert task class."""

    pass
