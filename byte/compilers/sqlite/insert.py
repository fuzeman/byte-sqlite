"""byte-sqlite - insert compiler module."""
from __future__ import absolute_import, division, print_function

from byte.compilers.sqlite.base import SqliteQueryCompiler
from byte.compilers.sqlite.models import SqliteClause, SqliteCommaSet, SqliteEnclosedSet, SqliteEntity
from byte.queries import InsertQuery


class SqliteInsertCompiler(SqliteQueryCompiler):
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

        columns = SqliteEnclosedSet(*[
            SqliteEntity(prop.name)
            for prop in query.state['properties']
        ])

        # Insert items in a single statement (SQLite 3.7.11+)
        if self.version >= (3, 7, 11):
            yield self.compile_all(query, columns, query.state['items'])
            return

        # Insert items with an individual statement (inside a transaction if there is multiple items)
        for item in query.state['items']:
            yield self.compile_one(query, columns, item)

    def compile_one(self, query, columns, item):
        # INSERT
        nodes = [SqliteClause('INSERT')]

        # TODO INSERT OR

        # INTO
        nodes.extend((
            SqliteClause('INTO'),
            SqliteEntity(self.table)
        ))

        # ROW
        row = []

        for prop in query.state['properties']:
            row.append(SqliteClause('?', item.get(prop.name)))

        # PROPERTIES, VALUES
        nodes.extend([
            columns,
            SqliteClause('VALUES'),
            SqliteEnclosedSet(*row)
        ])

        # TODO RETURNING

        # Compile nodes into SQLite Statement
        return self.compile_nodes(nodes)

    def compile_all(self, query, columns, items):
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

        for i, item in enumerate(items):
            row = []

            for prop in query.state['properties']:
                row.append(SqliteClause('?', item.get(prop.name)))

            rows.append(SqliteEnclosedSet(*row))

        # PROPERTIES, VALUES
        nodes.extend([
            columns,
            SqliteClause('VALUES'),
            SqliteCommaSet(*rows)
        ])

        # TODO RETURNING

        # Compile nodes into SQLite Statement
        return self.compile_nodes(nodes)
