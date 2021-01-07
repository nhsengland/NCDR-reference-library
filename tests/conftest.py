"""
Shared fixtures

Docs: https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions
"""

import pytest

from metrics.models import Lead, Metric, Operand, Organisation, Report, Team
from ncdr.models import (
    Column,
    ColumnImage,
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
def metric():
    denominator = Operand.objects.create(type="denominator")
    lead = Lead.objects.create(name="test lead")
    numerator = Operand.objects.create(type="numerator")
    organisation = Organisation.objects.create(name="test org")
    report = Report.objects.create(name="test report")
    team = Team.objects.create(name="test team")

    return Metric.objects.create(
        denominator=denominator,
        metric_lead=lead,
        numerator=numerator,
        organisation_owner=organisation,
        report=report,
        team_lead=team,
        indicator="test",
    )


@pytest.fixture
def published_column(published_table):
    return Column.objects.create(name="test", table=published_table)


@pytest.fixture
def published_data_element(published_column):
    data_element = DataElement.objects.create(name="test", slug="test")
    data_element.column_set.add(published_column)
    return data_element


@pytest.fixture
def published_database(published_version):
    return Database.objects.create(name="test", version=published_version)


@pytest.fixture
def published_grouping(published_data_element):
    grouping = Grouping.objects.create(name="test", slug="test")
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
    """
    The initial version is created by a database migration
    """
    return Version.objects.get(is_published=True)


@pytest.fixture
def unpublished_column(unpublished_table):
    return Column.objects.create(name="test", table=unpublished_table)


@pytest.fixture
def unpublished_data_element(unpublished_column):
    data_element = DataElement.objects.create(name="test", slug="test")
    data_element.column_set.add(unpublished_column)
    return data_element


@pytest.fixture
def unpublished_database(unpublished_version):
    return Database.objects.create(name="test", version=unpublished_version)


@pytest.fixture
def unpublished_grouping(unpublished_data_element):
    grouping = Grouping.objects.create(name="test", slug="test")
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
def column_image():
    column_image = ColumnImage.objects.create()
    column_image.columnimagerelation_set.create(
        database_name="test_db_name_1",
        schema_name="test_schema_name_1",
        table_name="test_table_name_1",
        column_name="test_column_name_1",
    )
    column_image.columnimagerelation_set.create(
        database_name="test_db_name_2",
        schema_name="test_schema_name_2",
        table_name="test_table_name_2",
        column_name="test_column_name_2",
    )
    return column_image


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
