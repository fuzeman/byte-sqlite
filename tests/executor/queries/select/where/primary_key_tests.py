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


def test_simple():
    """Test items can be retrieved by primary key."""
    users = Collection(User, 'sqlite://:memory:?table=users', plugins=[
        byte.compilers.sqlite,
        byte.executors.sqlite
    ])

    # Create table, and add items directly to database
    users.executor.connect().cursor().execute("""
        CREATE TABLE users (
            id          INTEGER         PRIMARY KEY AUTOINCREMENT NOT NULL,
            username    VARCHAR(255),
            password    VARCHAR(255)
        );
    """)

    with closing(users.executor.connect().cursor()) as cursor:
        cursor.execute("INSERT INTO users (id, username, password) VALUES (1, 'one', 'alpha');")
        cursor.execute("INSERT INTO users (id, username, password) VALUES (2, 'two', 'beta');")
        cursor.execute("INSERT INTO users (id, username, password) VALUES (3, 'three', 'charlie');")

    # Validate items
    user = users.select().where(User['id'] == 2).first()

    assert user is not None
    assert user.username == 'two'
    assert user.password == 'beta'
