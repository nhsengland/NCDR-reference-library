import datetime

from django.http.request import QueryDict
from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase
from csv_schema import models


class AbstractViewTestCase(TestCase):
    def setUp(self):
        self.csv_url = reverse('csv_page')
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
            data_dictionary_name="so,me data dictionary name",
            data_dictionary_link="http://data_dictionary_link.com",
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

    def get_csv_row_context(self, **get_args):
        qs = QueryDict(mutable=True)
        for k, v in get_args.items():
            qs[k] = v
        if get_args:
            url = "{}?{}".format(self.csv_url, qs.urlencode())
        else:
            url = self.csv_url
        response = self.client.get(url)
        return response.context


class IntegrationTestCase(AbstractViewTestCase):
    def test_about_page(self):
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, 200)

    def test_csv_page_empty(self):
        response = self.client.get(self.csv_url)
        self.assertEqual(response.status_code, 200)

    def test_csv_page_full(self):
        self.create_csv_rows(200)
        response = self.client.get(self.csv_url)
        self.assertEqual(response.status_code, 200)


class PaginatorTestCase(AbstractViewTestCase):

    def test_pagination_start(self):
        self.create_csv_rows(100)
        ctx = self.get_csv_row_context()
        self.assertEqual(
            list(ctx["max_page_range"]), [2, 3, 4, 5, 6]
        )

        self.assertEqual(
            list(ctx["min_page_range"]), []
        )
        self.assertEqual(ctx["object_list"].count(), 10)

    def test_pagination_middle(self):
        self.create_csv_rows(300)
        ctx = self.get_csv_row_context(page=15)
        self.assertEqual(
            list(ctx["max_page_range"]), [16, 17, 18, 19, 20]
        )

        self.assertEqual(
            list(ctx["min_page_range"]), [10, 11, 12, 13, 14]
        )
        self.assertEqual(ctx["object_list"].count(), 10)

    def test_pagination_end(self):
        self.create_csv_rows(144)
        ctx = self.get_csv_row_context(page=15)
        self.assertEqual(
            list(ctx["max_page_range"]), []
        )

        self.assertEqual(
            list(ctx["min_page_range"]), [10, 11, 12, 13, 14]
        )
        self.assertEqual(ctx["object_list"].count(), 4)

    def test_pagination_small(self):
        self.create_csv_rows(14)
        ctx = self.get_csv_row_context(page=2)
        self.assertEqual(
            list(ctx["max_page_range"]), []
        )

        self.assertEqual(
            list(ctx["min_page_range"]), [1]
        )
        self.assertEqual(ctx["object_list"].count(), 4)
