import datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.utils.functional import cached_property

from csv_schema import models
from ncdr.models import User
from ncdr.views import searchable_models


class AbstractViewTestCase(TestCase):
    EMAIL = "testuser"
    PASSWORD = "password"

    def setUp(self):
        self.database_list_url = reverse('database_list')
        self.about_url = reverse('about_page')
        self.client = Client()

    def create_name(self, idx):
        return "name_{}".format(idx)

    @cached_property
    def user(self):
        user = User.objects.create(
            email=self.EMAIL,
            is_staff=True,
            is_superuser=True
        )
        user.set_password(self.PASSWORD)
        user.save()
        return user

    def login(self):
        self.client.login(
            username=self.user.email, password=self.PASSWORD
        )

    def create_csv_column(
        self,
        column_args=None,
        database_name="example_db",
        schema_name="example_schema",
        table_name="example_table",
    ):
        database, _ = models.Database.objects.get_or_create(name=database_name)
        schema, _ = models.Schema.objects.get_or_create(
            name=schema_name,
            defaults={"database": database},
        )
        table, _ = models.Table.objects.get_or_create(
            name=table_name,
            schema=schema,
        )
        if not column_args:
            column_args = {}

        default_args = {
            "name": "some_item",
            "description": "some description",
            "technical_check": "some technical check",
            "is_derived_item": True,
            "definition_id": 1,
            "author": "Wilma Flintstone",
            "created_date_ext": datetime.date(2017, 1, 1),
            "table": table,
        }

        default_args.update(column_args)
        column = models.Column.objects.create(**default_args)
        return column

    def create_csv_columns(self, number, database=None, table=None):
        default_kwargs = {"column_args": {}}

        if database:
            default_kwargs["database"] = database

        if table:
            default_kwargs["table"] = table

        for i in range(number):
            default_kwargs["column_args"]["name"] = self.create_name(i)
            self.create_csv_column(**default_kwargs)


class ToggleModeSwitchTestCase(AbstractViewTestCase):
    def test_user_authenticated_on(self):
        url = reverse("toggle-preview-mode")
        url = url + "?next=/"
        self.login()

        self.assertFalse(User.objects.first().preview_mode)

        result = self.client.get(url)

        self.assertEqual(result.url, "/")
        self.assertTrue(User.objects.first().preview_mode)

    def test_user_authenticated_off(self):
        url = reverse("toggle-preview-mode")
        url = url + "?next=/"
        self.login()
        self.assertFalse(User.objects.first().preview_mode)

        self.user.toggle_preview_mode()

        result = self.client.get(url)
        self.assertEqual(result.url, "/")
        self.assertFalse(User.objects.first().preview_mode)

    def test_user_not_authenticated(self):
        url = reverse("toggle-preview-mode")
        result = self.client.get(url)
        self.assertEqual(result.url, '/accounts/login/?next=/toggle-preview-mode')


class PublishAllTestCase(AbstractViewTestCase):
    def test_publish_all(self):
        column = self.create_csv_column()
        column.published = False
        column.save()
        url = reverse('publish_all')
        url = url + "?next=/"
        self.login()
        result = self.client.post(url)
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.url, '/')
        self.assertTrue(
            models.Column.objects.get(id=column.id).published
        )

    def test_user_not_authenticated(self):
        url = reverse('publish_all')
        url = url + "?next=/"
        result = self.client.post(url)
        self.assertEqual(
            result.url, '/accounts/login/?next=/form/publish_all/%3Fnext%3D/'
        )


class UnpublishListTestCase(AbstractViewTestCase):
    url = reverse('unpublished_list', kwargs={"model_name": 'column'})

    def test_get(self):
        self.login()
        result = self.client.get(self.url)
        self.assertEqual(
            result.status_code, 200
        )

    def test_user_not_authenticated(self):
        result = self.client.get(self.url)
        self.assertEqual(
            result.url, '/accounts/login/?next=/form/column/unpublished/'
        )


class NCDRFormRedirectTestCase(AbstractViewTestCase):
    url = reverse('redirect')

    def test_get(self):
        self.login()
        result = self.client.get(self.url)
        self.assertEqual(
            result.status_code, 302
        )
        self.assertEqual(
            result.url, '/form/column/'
        )

    def test_user_not_authenticated(self):
        result = self.client.get(self.url)
        self.assertEqual(
            result.url, '/accounts/login/?next=/form/'
        )


class AbstractForm(object):
    def test_user_not_authenticated(self):
        url = self.get_url(model_name="column")
        result = self.client.get(url)
        self.assertEqual(
            result.url, '/accounts/login/?next={}'.format(url)
        )

    def test_get(self):
        self.login()
        for model in searchable_models:
            self.client.get(self.get_url(model_name=model.get_model_api_name()))


class NCDRAddManyViewTestCase(AbstractForm, AbstractViewTestCase):
    def get_url(self, model_name):
        return reverse("add_many", kwargs={"model_name": model_name})


class NCDREditViewTestCase(AbstractForm, AbstractViewTestCase):
    def setUp(self):
        super().setUp()
        column = self.create_csv_column()
        data_element = models.DataElement.objects.create(
            name="data_element",
            column=column,
        )
        models.Grouping.objects.create(
            name="grouping",
            dataelement=data_element
        )

    def get_url(self, model_name):
        return reverse("edit", kwargs={"model_name": model_name, "pk": 1})


class NCDREditListViewPopulatedTestCase(AbstractForm, AbstractViewTestCase):
    def setUp(self):
        super().setUp()
        column = self.create_csv_column()
        data_element = models.DataElement.objects.create(
            name="data_element",
            column=column,
        )
        models.Grouping.objects.create(
            name="grouping",
            dataelement=data_element
        )

    def get_url(self, model_name):
        return reverse("edit_list", kwargs={"model_name": model_name})


class NCDREditListEmptyTestCase(AbstractForm, AbstractViewTestCase):
    def get_url(self, model_name):
        return reverse("edit_list", kwargs={"model_name": model_name})


class NCDRSearchRedirect(AbstractViewTestCase):
    def setUp(self):
        super().setUp()
        self.create_csv_column()

    def get_url(self, search_term):
        url = reverse("search_redirect")
        return "{}?q={}".format(url, search_term)

    def test_get_with_column(self):
        column_name = models.Column.objects.get().name
        url = self.get_url(column_name)
        result = self.client.get(url)
        self.assertEqual(
            result.url,
            '/search/column/?q=some_item&search_option=Best%20Match'
        )

    def test_get_with_database(self):
        """ we should redirect to the existing field
            so if we don't match a column we should go
            straight to the first field that does match
        """
        database_name = models.Database.objects.get().name
        column_name = models.Column.objects.get().name

        # columns take priority over database so lets just make
        # sure the don't meet
        self.assertFalse(database_name == column_name)

        url = self.get_url(database_name)
        result = self.client.get(url)
        self.assertEqual(
            result.url,
            '/search/column/?q=example_db&search_option=Best%20Match'
        )


class NCDRSearch(AbstractViewTestCase):
    def get_url(self, model_name, query):
        url = reverse("search", kwargs={"model_name": model_name})
        return "{}?q={}".format(url, query)

    def get_test(self, query):
        for model in searchable_models:
            url = self.get_url(model_name=model.get_model_api_name(), query=query)
            result = self.client.get(url)
            self.assertEqual(result.status_code, 200)

    def test_get_empty(self):
        """ test all empty pages
        """
        for model in searchable_models:
            self.assertFalse(model.objects.exists())
        self.get_test("blah")

    def test_get_populated(self):
        """ test all pages when populated
        """
        column = self.create_csv_column()
        data_element = models.DataElement.objects.create(
            name="data_element",
            column=column,
        )
        models.Grouping.objects.create(
            name="grouping",
            dataelement=data_element
        )
        for model in searchable_models:
            model.objects.update(name="something")

        self.get_test("somethign")


class AboutTestCase(AbstractViewTestCase):
    def test_get(self):
        url = reverse("about_page")
        self.assertEqual(
            self.client.get(url).status_code,
            200
        )


class TableDetailTestCase(AbstractViewTestCase):
    def test_get_published(self):
        column = self.create_csv_column()
        column.published = True
        column.save()
        table = models.Table.objects.get()

        kwargs = {"db_name": table.schema.database.name, "pk": table.pk}
        url = reverse("table_detail", kwargs=kwargs)

        self.assertEqual(self.client.get(url).status_code, 200)

    def test_get_unpulished_not_in_preview_mode(self):
        column = self.create_csv_column()
        column.published = False
        column.save()
        table = models.Table.objects.get()

        kwargs = {"db_name": table.schema.database.name, "pk": table.pk}
        url = reverse("table_detail", kwargs=kwargs)

        self.assertEqual(self.client.get(url).status_code, 404)

    def test_get_unpublished_preview_mode(self):
        self.user.preview_mode = True
        self.user.save()

        self.login()
        column = self.create_csv_column()
        column.published = False
        column.save()
        table = models.Table.objects.get()

        kwargs = {"db_name": table.schema.database.name, "pk": table.pk}
        url = reverse("table_detail", kwargs=kwargs)

        self.assertEqual(self.client.get(url).status_code, 200)


class DatabaseDetailTestCase(AbstractViewTestCase):
    def test_get_published(self):
        column = self.create_csv_column()
        column.published = True
        column.save()
        database = models.Database.objects.get()
        url = reverse("database_detail", kwargs={"db_name": database.name})
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_get_unpulished_not_in_preview_mode(self):
        column = self.create_csv_column()
        column.published = False
        column.save()
        database = models.Database.objects.get()
        url = reverse("database_detail", kwargs={"db_name": database.name})
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_get_unpublished_preview_mode(self):
        self.user.preview_mode = True
        self.user.save()
        self.login()
        column = self.create_csv_column()
        column.published = False
        column.save()
        database = models.Database.objects.get()
        url = reverse("database_detail", kwargs={"db_name": database.name})
        self.assertEqual(self.client.get(url).status_code, 200)


class DataElementDetailTestCase(AbstractViewTestCase):
    def setUp(self):
        super().setUp()
        self.column = self.create_csv_column()
        self.data_element = models.DataElement.objects.create(
            name="something", description="blah"
        )
        self.column.data_element = self.data_element
        self.column.save()

    def test_get_published(self):
        self.column.published = True
        self.column.save()
        url = reverse("data_element_detail", kwargs={"slug": self.data_element.slug})
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_get_unpulished_not_in_preview_mode(self):
        self.column.published = False
        self.column.save()
        url = reverse("data_element_detail", kwargs={"slug": self.data_element.slug})
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_get_unpublished_preview_mode(self):
        self.user.preview_mode = True
        self.user.save()
        self.login()
        self.column.published = False
        self.column.save()
        url = reverse("data_element_detail", kwargs={"slug": self.data_element.slug})
        self.assertEqual(self.client.get(url).status_code, 200)


class DatabaseListTestCase(AbstractViewTestCase):
    def get_url(self):
        return reverse('database_list')

    def test_get_populated(self):
        self.create_csv_column()
        self.assertEqual(
            self.client.get(self.get_url()).status_code, 200
        )

    def test_get_empty(self):
        self.assertEqual(
            self.client.get(self.get_url()).status_code, 200
        )


class ColumnDetailTestCase(AbstractViewTestCase):
    def test_get_published(self):
        column = self.create_csv_column()
        column.published = True
        column.save()
        url = reverse("column_detail", kwargs={"pk": column.pk})
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_get_unpublished(self):
        column = self.create_csv_column()
        url = reverse("column_detail", kwargs={"pk": column.pk})
        self.assertEqual(self.client.get(url).status_code, 404)


class DataElementListTestCase(AbstractViewTestCase):
    def get_url(self):
        return reverse('data_element_list')

    def test_get_populated(self):
        self.column = self.create_csv_column()
        self.data_element = models.DataElement.objects.create(
            name="something", description="blah"
        )
        self.column.data_element = self.data_element
        self.column.save()
        self.assertEqual(
            self.client.get(self.get_url()).status_code, 200
        )

    def test_empty(self):
        self.assertEqual(
            self.client.get(self.get_url()).status_code, 200
        )


class IndexViewTestCase(AbstractViewTestCase):
    def get_url(self):
        return reverse('index_view')

    def test_redirect(self):
        expected = reverse('database_list')
        response = self.client.get(self.get_url())
        self.assertEqual(
            response.status_code, 302
        )
        self.assertEqual(
            response.url, expected
        )


class GroupingListViewTestCase(AbstractViewTestCase):
    def get_url(self):
        return reverse('grouping_redirect')

    def test_get_populated(self):
        self.column = self.create_csv_column()
        self.data_element = models.DataElement.objects.create(
            name="something", description="blah"
        )
        self.column.data_element = self.data_element
        self.column.save()
        self.grouping = models.Grouping.objects.create(
            name="grouping"
        )
        self.grouping.dataelement_set.add(self.data_element)
        self.assertEqual(
            self.client.get(self.get_url()).status_code, 200
        )

    def test_empty(self):
        self.assertEqual(
            self.client.get(self.get_url()).status_code, 200
        )


class GroupingDetailViewTestCase(AbstractViewTestCase):
    def setUp(self):
        super().setUp()
        self.column = self.create_csv_column()
        self.data_element = models.DataElement.objects.create(
            name="something", description="blah"
        )
        self.column.data_element = self.data_element
        self.column.save()
        self.grouping = models.Grouping.objects.create(
            name="grouping"
        )
        self.grouping.dataelement_set.add(self.data_element)

    def get_url(self):
        return reverse('grouping_detail', kwargs={"slug": self.grouping.slug})

    def test_get_published(self):
        self.column.published = True
        self.column.save()
        self.assertEqual(
            self.client.get(self.get_url()).status_code, 200
        )

    def test_unpublished(self):
        self.column.published = False
        self.column.save()
        self.assertEqual(
            self.client.get(self.get_url()).status_code, 404
        )
