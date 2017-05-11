"""byte-sqlite - executor package."""
from __future__ import absolute_import, division, print_function

from byte.executors.core.base import ExecutorPlugin


# TODO Implement SQLite executor
class SqliteExecutor(ExecutorPlugin):
    """SQLite executor class."""

    key = 'sqlite'
    priority = ExecutorPlugin.Priority.Low

    class Meta(ExecutorPlugin.Meta):
        """SQLite executor metadata."""

        content_type = 'application/x-sqlite3'  # noqa
        scheme       = 'sqlite'  # noqa

        extension = [
            'db',
            'sqlite'
        ]

    def construct_compiler(self):
        """Construct compiler."""
        return self.plugins.get_compiler('sqlite')(self)
