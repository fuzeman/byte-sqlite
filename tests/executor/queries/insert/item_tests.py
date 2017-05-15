from __future__ import absolute_import, division, print_function

from byte.collection import Collection
from byte.model import Model
from byte.property import Property
import byte.compilers.sqlite
import byte.executors.sqlite

from contextlib import closing


class User(Model):
    class Options:
        slots = True

    id = Property(int, primary_key=True)

    username = Property(str)
    password = Property(str)


def test_single():
    """Test single item can be inserted into a database."""
    users = Collection(User, 'sqlite://:memory:?table=users', plugins=[
        byte.compilers.sqlite,
        byte.executors.sqlite
    ])

    # Create table
    users.executor.connect().cursor().execute("""
        CREATE TABLE users (
            id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
            username    VARCHAR(255),
            password    VARCHAR(255)
        );
    """)

    # Insert item
    users.insert().items(
        {'username': 'one', 'password': 'alpha'}
    ).execute()

    # Validate item
    assert [(i.username, i.password) for i in users.all()] == [
        ('one', 'alpha')
    ]


def test_multiple():
    """Test multiple items can be inserted into a database."""
    users = Collection(User, 'sqlite://:memory:?table=users', plugins=[
        byte.compilers.sqlite,
        byte.executors.sqlite
    ])

    # Create table
    users.executor.connect().cursor().execute("""
        CREATE TABLE users (
            id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
            username    VARCHAR(255),
            password    VARCHAR(255)
        );
    """)

    # Insert items
    users.insert().items(
        {'username': 'one', 'password': 'alpha'},
        {'username': 'two', 'password': 'beta'},
        {'username': 'three', 'password': 'charlie'}
    ).execute()

    # Validate items
    assert [(i.username, i.password) for i in users.all()] == [
        ('one',     'alpha'),
        ('two',     'beta'),
        ('three',   'charlie')
    ]
