from byte.core.models import Node


class SqliteClause(Node):
    def __init__(self, value, *params):
        self.value = value
        self.params = params

    def compile(self):
        value = self.value

        if isinstance(value, Node):
            value, _ = value.compile()

        return str(value), self.params
