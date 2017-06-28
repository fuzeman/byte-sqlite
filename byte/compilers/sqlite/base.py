"""byte-sqlite - compiler base module."""
from __future__ import absolute_import, division, print_function

from byte.compilers.core.base import Compiler
from byte.compilers.sqlite.models import SqliteExpressions, SqliteSet
from byte.core.models.expressions.proxy import ProxyAnd


class BaseSqliteCompiler(Compiler):
    """Base SQLite compiler class."""

    def __init__(self, executor):
        """Create base SQLite compiler.

        :param executor: Executor
        :type executor: byte.executors.core.base.Executor
        """
        super(BaseSqliteCompiler, self).__init__(executor)

        self.table = self.engine.name

    def parse_expressions(self, expressions):
        """Parse proxy expressions into SQLite expressions.

        :param expressions: Expressions
        :type expressions: byte.base.BaseExpression

        :return: SQLite Nodes
        :rtype: byte.compilers.core.models.nodes.Node
        """
        return SqliteExpressions.parse(self, ProxyAnd(*expressions))

    @staticmethod
    def compile_nodes(nodes):
        """Compile nodes into SQLite statement.

        :param nodes: Nodes
        :type nodes: list of byte.compilers.core.models.nodes.Node

        :return: SQLite Statement
        :rtype: (str, tuple)
        """
        # Compile `nodes` into statement
        statement, parameters = SqliteSet(*nodes).compile()

        # Append ";" token to statement
        return statement + ';', parameters


class SqliteQueryCompiler(BaseSqliteCompiler):
    """SQLite query compiler class."""

    def __init__(self, compiler):
        """Create SQLite query compiler.

        :param compiler: SQLite Compiler
        :type compiler: SqliteCompiler
        """
        super(SqliteQueryCompiler, self).__init__(compiler.executor)

        self.compiler = compiler

    @property
    def version(self):
        """Retrieve SQLite syntax version.

        :rtype: tuple
        """
        return self.compiler.version
