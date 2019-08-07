# import pytest
# from django.urls import reverse

# # Tell pytest all tests in this file need DB access
# # Docs: https://pytest-django.readthedocs.io/en/latest/database.html#enabling-database-access-in-tests  # noqa: E501
# pytestmark = pytest.mark.django_db


# def test_metrics_detail(client, metric):
#     url = reverse("metrics-detail", kwargs={"pk": metric.pk})
#     resp = client.get(url)

#     assert resp.status_code == 200


# def test_metrics_list(client):
#     resp = client.get(reverse("metrics-list"))

#     assert resp.status_code == 200
