import pytest
from django.urls import reverse

from ncdr.models import User, Version

# Tell pytest all tests in this file need DB access
# Docs: https://pytest-django.readthedocs.io/en/latest/database.html#enabling-database-access-in-tests  # noqa: E501
pytestmark = pytest.mark.django_db


def test_publish_version(initial_version, client, user):
    client.force_login(user)

    version = Version.objects.create(is_published=False)

    url = reverse("publish_version", kwargs={"pk": version.pk})
    resp = client.post(url)

    assert resp.status_code == 302

    version = Version.objects.get(pk=version.pk)
    assert version.is_published


def test_publish_version_unauthenticated(initial_version, client):
    url = reverse("publish_version", kwargs={"pk": initial_version.pk})
    resp = client.post(url)

    assert resp.status_code == 302
    assert resp.url == f"/accounts/login/?next={url}"


def test_set_latest_version(initial_version, client, user):
    client.force_login(user)

    version = Version.objects.create(is_published=True)

    url = reverse("switch-to-latest-version")
    resp = client.get(url)

    assert resp.status_code == 302

    user = User.objects.get(pk=user.pk)
    assert user.current_version == version


def test_unpublished_versions(initial_version, client, unpublished_version, user):
    client.force_login(user)

    url = reverse("unpublished_list")
    resp = client.get(url)

    assert resp.status_code == 200


def test_unpublished_versions_unauthenticated(initial_version, client):
    url = reverse("unpublished_list")
    resp = client.post(url)

    assert resp.status_code == 302
    assert resp.url == f"/accounts/login/?next={url}"
