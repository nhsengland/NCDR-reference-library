import pytest
from django.urls import reverse

# Tell pytest all tests in this file need DB access
# Docs: https://pytest-django.readthedocs.io/en/latest/database.html#enabling-database-access-in-tests  # noqa: E501
pytestmark = pytest.mark.django_db


def test_grouping_detail_published(initial_version, client, published_grouping):
    url = reverse("grouping_detail", kwargs={"slug": published_grouping.slug})
    resp = client.get(url)

    assert resp.status_code == 200


def test_grouping_detail_unpublished(initial_version, client, unpublished_grouping):
    url = reverse("grouping_detail", kwargs={"slug": unpublished_grouping.slug})
    resp = client.get(url)

    assert resp.status_code == 404


def test_grouping_list_empty(initial_version, client):
    url = reverse("grouping_redirect")
    resp = client.get(url)

    assert resp.status_code == 200


def test_grouping_list_populated(initial_version, client, published_grouping):
    url = reverse("grouping_redirect")
    resp = client.get(url)

    assert resp.status_code == 200
