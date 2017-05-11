"""byte-sqlite - compiler module."""
from __future__ import absolute_import, division, print_function

from byte.compilers.core.base import CompilerPlugin
from byte.compilers.sqlite.base import BaseSqliteCompiler
from byte.compilers.sqlite.insert import SqliteInsertCompiler
from byte.compilers.sqlite.select import SqliteSelectCompiler
from byte.statements import InsertStatement, SelectStatement


class SqliteCompiler(CompilerPlugin, BaseSqliteCompiler):
    """SQLite compiler class."""

    key = 'sqlite'

    class Meta(CompilerPlugin.Meta):
        """SQLite compiler metadata."""

        content_type = 'application/x-sqlite3'

        extension = [
            'db',
            'sqlite'
        ]

    def __init__(self, executor):
        """Create SQLite compiler.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor
        """
        super(SqliteCompiler, self).__init__(executor)

        self.insert = SqliteInsertCompiler(executor)
        self.select = SqliteSelectCompiler(executor)

    def compile(self, statement):
        """Compile :code:`statement` into SQLite statement.

        :param statement: Statement
        :type statement: byte.statements.core.base.Statement

        :return: SQLite statement
        :rtype: tuple
        """
        if isinstance(statement, InsertStatement):
            return self.insert.compile(statement)

        if isinstance(statement, SelectStatement):
            return self.select.compile(statement)

        raise NotImplementedError
