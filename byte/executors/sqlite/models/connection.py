from byte.executors.core.models.database import DatabaseConnection
from byte.executors.sqlite.models.cursor import SqliteCursor


class SqliteConnection(DatabaseConnection):
    def __init__(self, executor, instance):
        super(SqliteConnection, self).__init__(executor)

        self.instance = instance

    def cursor(self):
        return SqliteCursor(
            self.executor,
            connection=self
        )

    def commit(self):
        self.instance.commit()

    def rollback(self):
        self.instance.rollback()
