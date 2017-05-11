from byte.compilers.core.base import CompilerPlugin
from byte.compilers.sqlite.base import BaseSqliteCompiler
from byte.compilers.sqlite.insert import SqliteInsertCompiler
from byte.compilers.sqlite.select import SqliteSelectCompiler
from byte.statements import InsertStatement, SelectStatement


class SqliteCompiler(CompilerPlugin, BaseSqliteCompiler):
    key = 'sqlite'

    class Meta(CompilerPlugin.Meta):
        content_type = 'application/x-sqlite3'

        extension = [
            'db',
            'sqlite'
        ]

    def __init__(self, executor):
        super(SqliteCompiler, self).__init__(executor)

        self.insert = SqliteInsertCompiler(executor)
        self.select = SqliteSelectCompiler(executor)

    def compile(self, statement):
        if isinstance(statement, InsertStatement):
            return self.insert.compile(statement)

        if isinstance(statement, SelectStatement):
            return self.select.compile(statement)

        raise NotImplementedError
