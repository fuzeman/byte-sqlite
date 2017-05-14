from byte.core.models import Node


class SqliteEntity(Node):
    def __init__(self, *path):
        self.path = path

    def compile(self):
        statement = '.'.join([
            '"%s"' % value
            for value in self.path
        ])

        return statement, tuple()
