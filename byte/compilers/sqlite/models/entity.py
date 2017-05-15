"""byte-sqlite - compiler entity model module."""
from __future__ import absolute_import, division, print_function

from byte.core.models import Node


class SqliteEntity(Node):
    """SQLite entity class."""

    def __init__(self, *path):
        """Create SQLite entity."""
        self.path = path

    def compile(self):
        """Compile SQLite entity.

        :rtype: (str, tuple)
        """
        statement = '.'.join([
            '"%s"' % value
            for value in self.path
        ])

        return statement, tuple()
