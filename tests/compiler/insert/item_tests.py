from __future__ import absolute_import, division, print_function

from byte.collection import Collection
from byte.compilers.sqlite import SqliteCompiler
from byte.model import Model
from byte.property import Property

from hamcrest import *


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_single():
    """Test insert query for a single item is complied correctly."""
    users = Collection(User, 'sqlite://:memory:?table=users')

    compiler = SqliteCompiler(
        users.executor,
        version=(3, 7, 11)
    )

    statements = list(compiler.compile(users.insert(
        User['username'],
        User['password']
    ).items(
        {'username': 'one', 'password': 'alpha'}
    )))

    assert_that(statements, equal_to([
        ('INSERT INTO "users" ("username", "password") VALUES (?, ?);', (
            'one', 'alpha'
        ))
    ]))


def test_single_legacy():
    """Test legacy insert query for a single item is complied correctly."""
    users = Collection(User, 'sqlite://:memory:?table=users')

    compiler = SqliteCompiler(
        users.executor,
        version=(3, 6, 0)
    )

    statements = list(compiler.compile(users.insert(
        User['username'],
        User['password']
    ).items(
        {'username': 'one', 'password': 'alpha'}
    )))

    assert_that(statements, equal_to([
        ('INSERT INTO "users" ("username", "password") VALUES (?, ?);', (
            'one', 'alpha'
        ))
    ]))


def test_multiple():
    """Test insert query for multiple items is complied correctly."""
    users = Collection(User, 'sqlite://:memory:?table=users')

    compiler = SqliteCompiler(
        users.executor,
        version=(3, 7, 11)
    )

    statements = list(compiler.compile(users.insert(
        User['username'],
        User['password']
    ).items(
        {'username': 'one', 'password': 'alpha'},
        {'username': 'two', 'password': 'beta'}
    )))

    assert_that(statements, equal_to([
        ('INSERT INTO "users" ("username", "password") VALUES (?, ?), (?, ?);', (
            'one', 'alpha',
            'two', 'beta'
        ))
    ]))


def test_multiple_legacy():
    """Test legacy insert query for multiple items is complied correctly."""
    users = Collection(User, 'sqlite://:memory:?table=users')

    compiler = SqliteCompiler(
        users.executor,
        version=(3, 6, 0)
    )

    statements = list(compiler.compile(users.insert(
        User['username'],
        User['password']
    ).items(
        {'username': 'one', 'password': 'alpha'},
        {'username': 'two', 'password': 'beta'}
    )))

    assert_that(statements, equal_to([
        ('INSERT INTO "users" ("username", "password") VALUES (?, ?);', ('one', 'alpha')),
        ('INSERT INTO "users" ("username", "password") VALUES (?, ?);', ('two', 'beta'))
    ]))
