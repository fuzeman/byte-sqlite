"""byte-sqlite - compiler module."""
from __future__ import absolute_import, division, print_function

from byte.compilers.core.base import CompilerPlugin
from byte.compilers.sqlite.base import BaseSqliteCompiler
from byte.compilers.sqlite.insert import SqliteInsertCompiler
from byte.compilers.sqlite.select import SqliteSelectCompiler
from byte.core.helpers.validate import is_tuple_of
from byte.core.plugin.base import Plugin
from byte.queries import InsertQuery, SelectQuery


class SqliteCompiler(CompilerPlugin, BaseSqliteCompiler):
    """SQLite compiler class."""

    class Meta(CompilerPlugin.Meta):
        """SQLite compiler metadata."""

        engine = Plugin.Engine.Table
        content_type = 'application/x-sqlite3'

        extension = [
            'db',
            'sqlite'
        ]

    def __init__(self, executor, version):
        """Create SQLite compiler.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor
        """
        super(SqliteCompiler, self).__init__(executor)

        self.version = version

        # Validate parameters
        if not is_tuple_of(self.version, int):
            raise ValueError('Invalid value provided for "version" parameter (expected tuple of int)')

        # Construct children
        self.insert = SqliteInsertCompiler(self)
        self.select = SqliteSelectCompiler(self)

    def compile(self, query):
        """Compile :code:`query` into SQLite statement.

        :param query: Query
        :type query: byte.queries.Query

        :return: SQLite statement
        :rtype: tuple
        """
        if isinstance(query, InsertQuery):
            return self.insert.compile(query)

        if isinstance(query, SelectQuery):
            return self.select.compile(query)

        raise NotImplementedError
