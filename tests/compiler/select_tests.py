from __future__ import absolute_import, division, print_function

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
    """Test select statement can be compiled to return all items."""
    users = Collection(User, 'sqlite://:memory:?table=users')

    sql, parameters = users.executor.compiler.compile(users.all())

    assert_that(sql, equal_to('SELECT * FROM "users";'))
    assert_that(parameters, equal_to(tuple()))
