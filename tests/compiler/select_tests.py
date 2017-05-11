from byte.collection import Collection
from byte.model import Model
from byte.property import Property

from hamcrest import *


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_all():
    users = Collection(User, 'sqlite://:memory:?table=users')

    sql, parameters = users.executor.compiler.compile(users.all())

    assert_that(sql, equal_to('SELECT * FROM "users";'))
    assert_that(parameters, equal_to(tuple()))
