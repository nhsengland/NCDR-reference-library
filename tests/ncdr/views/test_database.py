import pytest
from django.urls import reverse

# Tell pytest all tests in this file need DB access
# Docs: https://pytest-django.readthedocs.io/en/latest/database.html#enabling-database-access-in-tests  # noqa: E501
pytestmark = pytest.mark.django_db


def test_database_detail_published_version(initial_version, client, published_database):
    url = reverse("database_detail", kwargs={"db_name": published_database.name})
    resp = client.get(url)

    assert resp.status_code == 200


def test_database_detail_unpublished_version(
    initial_version, client, unpublished_database
):
    url = reverse("database_detail", kwargs={"db_name": unpublished_database.name})
    resp = client.get(url)

    assert resp.status_code == 404


def test_database_list_populated(initial_version, client):
    url = reverse("database_list")
    resp = client.get(url)

    assert resp.status_code == 200


def test_database_list_empty(initial_version, client):
    url = reverse("database_list")
    resp = client.get(url)

    assert resp.status_code == 200
