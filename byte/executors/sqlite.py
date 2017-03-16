from __future__ import absolute_import, division, print_function

from byte.executors.core.base import ExecutorPlugin


class SqliteExecutor(ExecutorPlugin):
    key = 'sqlite'
    priority = ExecutorPlugin.Priority.Low

    class Meta(ExecutorPlugin.Meta):
        content_type = 'application/x-sqlite3'
        scheme =       'sqlite'

        extension = [
            'db',
            'sqlite'
        ]
