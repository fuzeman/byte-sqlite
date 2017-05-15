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


def test_insert():
    """Test insert query is complied correctly."""
    users = Collection(User, 'sqlite://:memory:?table=users')

    sql, parameters = users.executor.compiler.compile(users.insert(
        User['username'],
        User['password']
    ).items({
        'username': 'one',
        'password': 'two'
    }))

    assert_that(sql, equal_to('INSERT INTO "users" ("username", "password") VALUES (?, ?);'))
    assert_that(parameters, equal_to(('one', 'two')))
