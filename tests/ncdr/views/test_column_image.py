import json
from tempfile import NamedTemporaryFile

import pytest
from django.urls import reverse

from ncdr.models import Column, ColumnImage

# Tell pytest all tests in this file need DB access
# Docs: https://pytest-django.readthedocs.io/en/latest/database.html#enabling-database-access-in-tests  # noqa: E501
pytestmark = pytest.mark.django_db


def test_column_image_list(column_image, client, user):
    client.force_login(user)
    url = reverse("column_image_list")
    resp = client.get(url)
    assert resp.status_code == 200
    context = resp.context
    assert len(context["object_list"]) == 1
    assert context["object_list"][0].id == column_image.id


def test_column_image_list_none(client, user):
    client.force_login(user)
    url = reverse("column_image_list")
    resp = client.get(url)
    assert resp.status_code == 200
    context = resp.context
    assert len(context["object_list"]) == 0


def test_column_path_option_list_get(published_table, client, user):
    Column.objects.create(name="test_column_name_1", table=published_table)
    Column.objects.create(name="test_column_name_2", table=published_table)
    client.force_login(user)
    url = reverse("column_path_options_list")
    resp = client.get(url)
    assert resp.status_code == 200
    context = resp.json()
    assert len(context["results"]) == 2
    names = [i["text"] for i in context["results"]]
    assert names == ["test_column_name_1", "test_column_name_2"]
    assert not context["pagination"]["more"]


def test_column_path_option_list_query(published_table, client, user):
    Column.objects.create(name="test_column_name_1", table=published_table)
    Column.objects.create(name="test_column_name_2", table=published_table)
    client.force_login(user)
    url = reverse("column_path_options_list")
    url = url + "?q=column_name_1"
    resp = client.get(url)
    assert resp.status_code == 200
    context = resp.json()
    assert len(context["results"]) == 1
    names = [i["text"] for i in context["results"]]
    assert names == ["test_column_name_1"]
    assert not context["pagination"]["more"]


def test_get_column_image_edit(column_image, client, user):
    client.force_login(user)
    url = reverse("column_image_edit", kwargs={"pk": column_image.id})
    resp = client.get(url)
    assert resp.status_code == 200


def test_post_column_image(column_image, client, user):
    client.force_login(user)
    tmp_file = NamedTemporaryFile(suffix=".jpg")
    with open(tmp_file.name, "w") as tf:
        tf.write("something")

    url = reverse("column_image_edit", kwargs={"pk": column_image.id})
    with open(tmp_file.name) as tf:
        post_dict = {
            "id": column_image.id,
            "image": tf,
            "relation": [
                json.dumps(
                    [
                        "new_db_name",
                        "new_schema_name",
                        "new_table_name",
                        "new_column_name",
                    ]
                )
            ],
        }
        resp = client.post(url, post_dict)
    assert resp.status_code == 302
    column_image = ColumnImage.objects.get(id=column_image.id)
    relation = column_image.columnimagerelation_set.get()
    assert resp.status_code == 302
    assert relation.database_name == "new_db_name"
    assert relation.schema_name == "new_schema_name"
    assert relation.table_name == "new_table_name"
    assert relation.column_name == "new_column_name"


def test_get_column_image_delete(column_image, client, user):
    client.force_login(user)
    url = reverse("column_image_delete", kwargs={"pk": column_image.id})
    resp = client.get(url)
    assert resp.status_code == 200


def test_post_column_image_delete(column_image, client, user):
    client.force_login(user)
    url = reverse("column_image_delete", kwargs={"pk": column_image.id})
    resp = client.post(url)
    assert resp.status_code == 302
    assert ColumnImage.objects.count() == 0
