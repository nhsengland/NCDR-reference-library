import pytest
from django.urls import reverse

# Tell pytest all tests in this file need DB access
# Docs: https://pytest-django.readthedocs.io/en/latest/database.html#enabling-database-access-in-tests  # noqa: E501
pytestmark = pytest.mark.django_db


def test_table_detail_published(initial_version, client, published_table):
    database_name = published_table.schema.database.name

    url = reverse(
        "table_detail", kwargs={"db_name": database_name, "pk": published_table.pk}
    )
    resp = client.get(url)

    assert resp.status_code == 200


def test_table_detail_unpublished(initial_version, client, unpublished_table):
    database_name = unpublished_table.schema.database.name

    url = reverse(
        "table_detail", kwargs={"db_name": database_name, "pk": unpublished_table.pk}
    )
    resp = client.get(url)

    assert resp.status_code == 404
