from byte.compilers.core.base import Compiler
from byte.compilers.sqlite.base import BaseSqliteCompiler
from byte.statements import SelectStatement


class SqliteSelectCompiler(Compiler, BaseSqliteCompiler):
    def compile(self, statement):
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
