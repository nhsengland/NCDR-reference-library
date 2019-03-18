import pytest
from django.urls import reverse

# Tell pytest all tests in this file need DB access
# Docs: https://pytest-django.readthedocs.io/en/latest/database.html#enabling-database-access-in-tests  # noqa: E501
pytestmark = pytest.mark.django_db


def test_search_redirect_column(initial_version, client, published_column):
    url = f"{reverse('search_redirect')}?q={published_column.name}"
    resp = client.get(url)

    assert resp.url == "/search/column/?q=test"


def test_search_redirect_database(initial_version, client, published_database):
    url = f"{reverse('search_redirect')}?q={published_database.name}"
    resp = client.get(url)

    assert resp.url == "/search/column/?q=test"


def test_search_empty(initial_version, client):
    for name in ["column", "database", "dataelement", "grouping", "table"]:
        base = reverse("search", kwargs={"model_name": name})
        url = f"{base}?q=blah"
        resp = client.get(url)

        assert resp.status_code == 200


def test_search_populated(initial_version, client, published_column):
    for name in ["column", "database", "dataelement", "grouping", "table"]:
        base = reverse("search", kwargs={"model_name": name})
        url = f"{base}?q=test"  # fixtured models all have the name test
        resp = client.get(url)

        assert resp.status_code == 200
