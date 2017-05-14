from byte.core.models import Node


class SqliteClause(Node):
    def __init__(self, value, *params):
        self.value = value
        self.params = params

    def compile(self):
        return str(self.value), self.params

    def __str__(self):
        return str(self.value)
