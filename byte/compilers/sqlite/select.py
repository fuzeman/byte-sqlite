"""byte-sqlite - select compiler module."""
from __future__ import absolute_import, division, print_function

from byte.compilers.sqlite.base import BaseSqliteCompiler
from byte.compilers.sqlite.models import SqliteClause, SqliteCommaSet, SqliteEntity
from byte.queries import SelectQuery


class SqliteSelectCompiler(BaseSqliteCompiler):
    """SQLite select statement compiler class."""

    def compile(self, query):
        """Compile :code:`query` into SQLite query.

        :param query: Select Query
        :type query: byte.queries.SelectQuery

        :return: SQLite Statement
        :rtype: (str, tuple)
        """
        if not isinstance(query, SelectQuery):
            raise ValueError('Invalid value provided for "query" (expected SelectQuery instance)')

        # SELECT / SELECT DISTINCT
        if query.state['distinct']:
            nodes = [SqliteClause('SELECT DISTINCT')]
        else:
            nodes = [SqliteClause('SELECT')]

        # PROPERTIES
        if query.state['properties'] is not None:
            nodes.append(SqliteCommaSet(*query.state['properties']))
        else:
            nodes.append(SqliteClause('*'))

        # FROM
        nodes.append(SqliteClause('FROM'))

        if query.state['from']:
            nodes.append(SqliteCommaSet(*tuple([
                SqliteEntity(value)
                for value in query.state['from']
            ])))
        else:
            nodes.append(SqliteEntity(self.table))

        # TODO JOIN

        # WHERE
        if query.state['where']:
            nodes.extend((
                SqliteClause('WHERE'),
                self.parse_expressions(query.state['where'])
            ))

        # GROUP BY
        if query.state['group_by']:
            nodes.extend((
                SqliteClause('GROUP BY'),
                SqliteCommaSet(*query.state['group_by'])
            ))

        # TODO HAVING

        # TODO WINDOW

        # ORDER BY
        if query.state['order_by']:
            nodes.extend((
                SqliteClause('ORDER BY'),
                SqliteCommaSet(*query.state['order_by'])
            ))

        # LIMIT
        if query.state['limit'] is not None:
            nodes.append(SqliteClause('LIMIT ?', query.state['limit']))

        # OFFSET
        if query.state['offset'] is not None:
            nodes.append(SqliteClause('OFFSET ?', query.state['offset']))

        # TODO for_update

        # Compile nodes into SQLite Statement
        return self.compile_nodes(nodes)
