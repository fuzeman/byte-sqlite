from __future__ import absolute_import, division, print_function

from byte.table import Model, Property, Table
import byte.compilers.sqlite
import byte.executors.sqlite

from hamcrest import *


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_all():
    """Test all items can be retrieved from database."""
    users = Table(User, 'sqlite://:memory:', name='users', plugins=[
        byte.compilers.sqlite,
        byte.executors.sqlite
    ])

    # Create table, and add items directly to database
    with users.executor.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE users (
                    id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username    VARCHAR(255),
                    password    VARCHAR(255)
                );
            """)

            cursor.execute("INSERT INTO users (username, password) VALUES ('one', 'alpha');")
            cursor.execute("INSERT INTO users (username, password) VALUES ('two', 'beta');")
            cursor.execute("INSERT INTO users (username, password) VALUES ('three', 'charlie');")

    # Validate items
    assert_that(users.all(), only_contains(
        has_properties({
            'username': 'one',
            'password': 'alpha'
        }),
        has_properties({
            'username': 'two',
            'password': 'beta'
        }),
        has_properties({
            'username': 'three',
            'password': 'charlie'
        })
    ))


def test_get():
    """Test single item can be retrieved from database."""
    users = Table(User, 'sqlite://:memory:', name='users', plugins=[
        byte.compilers.sqlite,
        byte.executors.sqlite
    ])

    # Create table, and add items directly to database
    with users.executor.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE users (
                    id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username    VARCHAR(255),
                    password    VARCHAR(255)
                );
            """)

            cursor.execute("INSERT INTO users (id, username, password) VALUES (1, 'one', 'alpha');")
            cursor.execute("INSERT INTO users (id, username, password) VALUES (2, 'two', 'beta');")
            cursor.execute("INSERT INTO users (id, username, password) VALUES (3, 'three', 'charlie');")

    # Validate items
    user = users.get(User['id'] == 2)

    assert_that(user, all_of(
        not_none(),
        has_properties({
            'username': 'two',
            'password': 'beta'
        })
    ))
