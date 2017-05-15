"""byte-sqlite - compiler clause model module."""
from __future__ import absolute_import, division, print_function

from byte.core.models import Node


class SqliteClause(Node):
    """SQLite clause class."""

    def __init__(self, value, *params):
        """Create SQLite clause.

        :param value: Value
        :type value: str
        """
        self.value = value
        self.params = params

    def compile(self):
        """Compile SQLite clause.

        :rtype: (str, tuple)
        """
        value = self.value

        if isinstance(value, Node):
            value, _ = value.compile()

        return str(value), self.params
