from byte.compilers.core.base import Compiler
from byte.compilers.sqlite.base import BaseSqliteCompiler, Clause
from byte.statements import InsertStatement


class SqliteInsertCompiler(BaseSqliteCompiler):
    def compile(self, statement):
        if not isinstance(statement, InsertStatement):
            raise ValueError('Invalid value provided for "query" (expected InsertQuery instance)')

        clauses = ['INSERT']

        clauses.append('INTO')
        clauses.append('"%s"' % self.table)

        clauses.append('(%s)' % (
            ', '.join([
                '"%s"."%s"' % (
                    self.table,
                    key
                )
                for key, prop in self.model.Internal.properties_by_name.items()
                if not prop.primary_key
            ])
        ))

        clauses.append('VALUES')

        for i, item in enumerate(statement.items):
            parameters = []

            for key, prop in self.model.Internal.properties_by_name.items():
                if prop.primary_key:
                    continue

                parameters.append(item.get(key))

            clauses.append(Clause(
                '(%s)%s' % (
                    ', '.join(['?' for _ in parameters]),
                    ',' if i < len(statement.items) - 1 else ''
                ),
                *parameters
            ))

        return self.join(clauses)
