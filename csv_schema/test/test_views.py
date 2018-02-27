import datetime

from django.urls import reverse
from django.test import Client
from django.test import TestCase
from csv_schema import models


class AbstractViewTestCase(TestCase):
    def setUp(self):
        self.database_list_url = reverse('database_list')
        self.about_url = reverse('about_page')
        self.client = Client()

    def create_name(self, idx):
        return "name_{}".format(idx)

    def create_csv_column(
        self, column_args=None, database="example_db", table="example_table"
    ):
        db, _ = models.Database.objects.get_or_create(name=database)
        table, _ = models.Table.objects.get_or_create(
            name=table,
            database=db
        )
        if not column_args:
            column_args = {}

        default_args = dict(
            name="some_item",
            description="some description",
            technical_check="some technical check",
            is_derived_item=True,
            definition_id=1,
            author="Wilma Flintstone",
            created_date_ext=datetime.date(2017, 1, 1)
        )

        default_args.update(column_args)
        column = models.Column.objects.create(**default_args)
        column.tables.add(table)
        return column

    def create_csv_columns(self, number, database=None, table=None):
        default_kwargs = dict(column_args={})

        if database:
            default_kwargs["database"] = database

        if table:
            default_kwargs["table"] = table

        for i in range(number):
            default_kwargs["column_args"]["name"] = self.create_name(i)
            self.create_csv_column(**default_kwargs)


class ViewsTestCase(AbstractViewTestCase):
    def test_about_page(self):
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, 200)

    def test_database_list_empty(self):
        response = self.client.get(self.database_list_url)
        self.assertEqual(response.status_code, 200)

    def test_database_list_full(self):
        self.create_csv_columns(200)
        response = self.client.get(self.database_list_url)
        self.assertEqual(response.status_code, 200)

    def test_database_detail(self):
        self.create_csv_column()
        url = reverse("database_detail", kwargs=dict(db_name='example_db'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_table_detail(self):
        """ should provide a context of all tables under that
            database that are not empty
        """
        row_1 = self.create_csv_column()
        row_2 = self.create_csv_column(
            column_args=dict(name="other_row"), table="example_table_2"
        )

        # an empty table
        models.Table.objects.create(
            database=row_1.tables.first().database, name="empty"
        )
        self.create_csv_column(
            column_args=dict(name="other_db"),
            database="example_db_2", table="example_table"
        )
        url = reverse("table_detail", kwargs=dict(
            db_name='example_db',
            table_name='example_table'
        ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context_data["tables"].values_list("id", flat=True)),
            [row_1.id, row_2.id]
        )

    def test_ncdr_references_redirect(self):
        column = self.create_csv_column(column_args=dict(name="Aadvark"))
        db = models.Database.objects.create(name="some_other_db")
        table = models.Table.objects.create(
            database=db, name="some_other_table"
        )
        column.tables.add(table)
        url = reverse(
            "column_redirect"
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(
            response.redirect_chain,
            [('/ncdr_references/A', 302)]
        )

    def test_ncdr_reference_view(self):
        column = self.create_csv_column(column_args=dict(name="ba barackus"))
        db = models.Database.objects.create(name="some_other_db")
        table = models.Table.objects.create(
            database=db, name="some_other_table"
        )
        column.tables.add(table)
        url = reverse('column_list', kwargs=dict(letter="B"))
        response = self.client.get(url)
        expected_column = response.context_data["object_list"].get()
        self.assertEqual(
            expected_column, column
        )
