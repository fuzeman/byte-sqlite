from byte.executors.core.models.database import DatabaseCursor


class SqliteCursor(DatabaseCursor):
    def __init__(self, executor, connection=None, connection_detach=None):
        super(SqliteCursor, self).__init__(executor)

        self.connection = connection
        self.connection_detach = connection_detach

        # Retrieve connection from executor (if one wasn't provided)
        if not self.connection:
            self.connection = self.executor.connection()
            self.connection_detach = True

        # Create cursor
        self.instance = self.connection.instance.cursor()

    @property
    def columns(self):
        return self.instance.description

    def execute(self, statement, parameters=None):
        if not parameters:
            return self.instance.execute(statement)

        return self.instance.execute(statement, parameters)

    def close(self):
        self.close_connection()
        self.close_cursor()

    def close_connection(self):
        if not self.connection:
            return

        # Detach connection from thread (if enabled)
        if self.connection_detach:
            self.connection.detach()

        # Remove connection reference
        self.connection = None

    def close_cursor(self):
        if not self.instance:
            return

        # Close cursor
        self.instance.close()

        # Remove cursor reference
        self.instance = None

    def __iter__(self):
        return iter(self.instance)
