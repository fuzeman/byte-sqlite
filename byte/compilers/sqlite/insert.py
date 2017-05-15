"""byte-sqlite - insert compiler module."""
from __future__ import absolute_import, division, print_function

from byte.compilers.sqlite.base import BaseSqliteCompiler
from byte.compilers.sqlite.models import SqliteClause, SqliteCommaSet, SqliteEnclosedSet, SqliteEntity
from byte.queries import InsertQuery


class SqliteInsertCompiler(BaseSqliteCompiler):
    """SQLite insert statement compiler class."""

    def compile(self, query):
        """Compile :code:`query` into SQLite statement.

        :param query: Insert Query
        :type query: byte.queries.InsertQuery

        :return: SQLite statement
        :rtype: tuple
        """
        if not isinstance(query, InsertQuery):
            raise ValueError('Invalid value provided for "query" (expected InsertQuery instance)')

        # INSERT
        nodes = [SqliteClause('INSERT')]

        # TODO INSERT OR

        # INTO
        nodes.extend((
            SqliteClause('INTO'),
            SqliteEntity(self.table)
        ))

        # ROWS
        rows = []

        for i, item in enumerate(query.state['items']):
            row = []

            for prop in query.state['properties']:
                row.append(SqliteClause('?', item.get(prop.name)))

            rows.append(SqliteEnclosedSet(*row))

        # PROPERTIES, VALUES
        nodes.extend([
            SqliteEnclosedSet(*[
                SqliteEntity(prop.name)
                for prop in query.state['properties']
            ]),
            SqliteClause('VALUES'),
            SqliteCommaSet(*rows)
        ])

        # TODO RETURNING

        # Compile nodes into SQLite Statement
        return self.compile_nodes(nodes)
