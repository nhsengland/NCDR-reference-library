import datetime

from django.http.request import QueryDict
from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase
from csv_schema import models


class AbstractViewTestCase(TestCase):
    def setUp(self):
        self.database_list_url = reverse('database_list')
        self.about_url = reverse('about_page')
        self.client = Client()

    def create_data_item(self, idx):
        return "data_item_{}".format(idx)

    def create_csv_row(self, row_args, database="example", table="example"):
        db, _ = models.Database.objects.get_or_create(name=database)
        table, _ = models.Table.objects.get_or_create(
            name=table,
            database=db
        )
        default_args = dict(
            table=table,
            data_item="some_item",
            description="some description",
            technical_check="some technical check",
            is_derived_item=True,
            definition_id=1,
            author="Wilma Flintstone",
            created_date_ext=datetime.date(2017, 1, 1)
        )

        default_args.update(row_args)
        return models.Row.objects.create(**default_args)

    def create_csv_rows(self, number, database=None, table=None):
        default_kwargs = dict(row_args={})

        if database:
            default_kwargs["database"] = database

        if table:
            default_kwargs["table"] = table

        for i in range(number):
            default_kwargs["row_args"]["data_item"] = self.create_data_item(i)
            self.create_csv_row(**default_kwargs)


class IntegrationTestCase(AbstractViewTestCase):
    def test_about_page(self):
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, 200)

    def test_csv_page_empty(self):
        response = self.client.get(self.database_list_url)
        self.assertEqual(response.status_code, 200)

    def test_csv_page_full(self):
        self.create_csv_rows(200)
        response = self.client.get(self.database_list_url)
        self.assertEqual(response.status_code, 200)
