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
    """Test select query can be compiled to return all items."""
    users = Collection(User, 'sqlite://:memory:?table=users')

    statements = list(users.executor.compiler.compile(users.all()))

    assert_that(statements, equal_to([
        ('SELECT * FROM "users";', ())
    ]))


def test_where():
    """Test select query with where expressions can be compiled."""
    users = Collection(User, 'sqlite://:memory:?table=users')

    statements = list(users.executor.compiler.compile(users.select().where(
        User['id'] == 142
    )))

    assert_that(statements, equal_to([
        ('SELECT * FROM "users" WHERE "users"."id" == ?;', (142,))
    ]))
