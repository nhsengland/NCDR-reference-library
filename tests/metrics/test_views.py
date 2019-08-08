import pytest
from django.urls import reverse

from metrics.models import Metric

# # Tell pytest all tests in this file need DB access
# # Docs: https://pytest-django.readthedocs.io/en/latest/database.html#enabling-database-access-in-tests  # noqa: E501
pytestmark = pytest.mark.django_db


def test_metrics_detail(client, metric):
    url = reverse("metrics-detail", kwargs={"pk": metric.pk})
    resp = client.get(url)

    assert resp.status_code == 200


def test_metrics_list(client):
    resp = client.get(reverse("metrics-list"))
    assert resp.status_code == 200


def test_about(client):
    resp = client.get(reverse("metrics-about"))
    assert resp.status_code == 200


def test_search_empty(client):
    base_url = reverse("metrics-search")
    url = f"{base_url}?q=test"
    resp = client.get(url)
    assert resp.status_code == 200
    assert list(resp.context_data["object_list"]) == []


def test_search_populated(metric, client):
    base_url = reverse("metrics-search")
    url = f"{base_url}?q=test"
    resp = client.get(url)
    assert list(resp.context_data["object_list"]) == [Metric.objects.get()]
    assert resp.status_code == 200
