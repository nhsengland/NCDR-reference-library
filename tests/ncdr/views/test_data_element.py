import pytest
from django.urls import reverse

# Tell pytest all tests in this file need DB access
# Docs: https://pytest-django.readthedocs.io/en/latest/database.html#enabling-database-access-in-tests  # noqa: E501
pytestmark = pytest.mark.django_db


def test_data_element_detail_published(initial_version, client, published_data_element):
    url = reverse("data_element_detail", kwargs={"slug": published_data_element.slug})
    resp = client.get(url)

    assert resp.status_code == 200


def test_data_element_detail_unpublished(
    initial_version, client, unpublished_data_element
):
    url = reverse("data_element_detail", kwargs={"slug": unpublished_data_element.slug})
    resp = client.get(url)

    assert resp.status_code == 404


def test_data_element_list_empty(initial_version, client):
    url = reverse("data_element_list")
    resp = client.get(url)

    assert resp.status_code == 200


def test_data_element_list_populated(initial_version, client, published_data_element):
    url = reverse("data_element_list")
    resp = client.get(url)

    assert resp.status_code == 200
