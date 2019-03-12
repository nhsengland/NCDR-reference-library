import pytest
from django.urls import reverse

# Tell pytest all tests in this file need DB access
# Docs: https://pytest-django.readthedocs.io/en/latest/database.html#enabling-database-access-in-tests  # noqa: E501
pytestmark = pytest.mark.django_db


def test_about(initial_version, client):
    url = reverse("about_page")
    resp = client.get(url)

    assert resp.status_code == 200


def test_column_detail_published_version(initial_version, client, published_column):
    database_name = published_column.table.schema.database.name
    url = reverse(
        "column_detail", kwargs={"db_name": database_name, "pk": published_column.pk}
    )
    resp = client.get(url)

    assert resp.status_code == 200


def test_column_detail_unpublished_version(initial_version, client, unpublished_column):
    database_name = unpublished_column.table.schema.database.name
    url = reverse(
        "column_detail", kwargs={"db_name": database_name, "pk": unpublished_column.pk}
    )
    resp = client.get(url)

    assert resp.status_code == 404


def test_index_view(initial_version, client):
    url = reverse("index_view")
    resp = client.get(url)

    assert resp.status_code == 302
    assert resp.url == reverse("database_list")
