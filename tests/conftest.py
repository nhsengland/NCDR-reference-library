"""
Shared fixtures

Docs: https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions
"""

import pytest

from ncdr.models import (
    Column,
    Database,
    DataElement,
    Grouping,
    Schema,
    Table,
    User,
    Version,
)


@pytest.fixture
def initial_version(published_version):
    """
    Provide an "initial" published Version

    This project provides a Version object on requests via a middleware so one
    can get the latest published version site wide.  However this requires a
    Version in the database.  Changing the middleware to return `version =
    None` pushes handling the None case into the views but isn't a situation
    that would happen in the running of the site.  So instead the tests should
    deal with that situation since they "caused" it.
    """
    return published_version


@pytest.fixture
def published_column(published_table):
    return Column.objects.create(name="test", table=published_table)


@pytest.fixture
def published_data_element(published_column):
    data_element = DataElement.objects.create(name="test")
    data_element.column_set.add(published_column)
    return data_element


@pytest.fixture
def published_database(published_version):
    return Database.objects.create(name="test", version=published_version)


@pytest.fixture
def published_grouping(published_data_element):
    grouping = Grouping.objects.create(name="test")
    grouping.dataelement_set.add(published_data_element)
    return grouping


@pytest.fixture
def published_schema(published_database):
    return Schema.objects.create(name="test", database=published_database)


@pytest.fixture
def published_table(published_schema):
    return Table.objects.create(name="test", schema=published_schema)


@pytest.fixture
def published_version():
    return Version.objects.create(is_published=True)


@pytest.fixture
def unpublished_column(unpublished_table):
    return Column.objects.create(name="test", table=unpublished_table)


@pytest.fixture
def unpublished_data_element(unpublished_column):
    data_element = DataElement.objects.create(name="test")
    data_element.column_set.add(unpublished_column)
    return data_element


@pytest.fixture
def unpublished_database(unpublished_version):
    return Database.objects.create(name="test", version=unpublished_version)


@pytest.fixture
def unpublished_grouping(unpublished_data_element):
    grouping = Grouping.objects.create(name="test")
    grouping.dataelement_set.add(unpublished_data_element)
    return grouping


@pytest.fixture
def unpublished_schema(unpublished_database):
    return Schema.objects.create(name="test", database=unpublished_database)


@pytest.fixture
def unpublished_table(unpublished_schema):
    return Table.objects.create(name="test", schema=unpublished_schema)


@pytest.fixture
def unpublished_version():
    return Version.objects.create(is_published=False)


@pytest.fixture
def user(initial_version):
    user = User.objects.create(
        email="test@test.com",
        is_staff=True,
        is_superuser=True,
        current_version=initial_version,
    )

    user.set_password("test")
    user.save()

    return user
