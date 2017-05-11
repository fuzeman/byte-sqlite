"""byte-sqlite - select compiler module."""
from __future__ import absolute_import, division, print_function

from byte.compilers.sqlite.base import BaseSqliteCompiler
from byte.statements import SelectStatement


class SqliteSelectCompiler(BaseSqliteCompiler):
    """SQLite select statement compiler class."""

    def compile(self, statement):
        """Compile :code:`statement` into SQLite statement.

        :param statement: Select Statement
        :type statement: byte.statements.SelectStatement

        :return: SQLite statement
        :rtype: tuple
        """
        if not isinstance(statement, SelectStatement):
            raise ValueError('Invalid value provided for "query" (expected SelectQuery instance)')

        clauses = ['SELECT']

        self.add_properties(clauses, statement.properties)

        clauses.append('FROM')
        clauses.append('"%s"' % self.table)

        if statement.state.get('where'):
            clauses.append('WHERE')
            clauses.append(self.join('AND', self.encode_expressions(statement.state['where'])))

        return self.merge(clauses)
