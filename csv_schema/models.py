# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import functools
import operator
from django.contrib.auth.signals import user_logged_out
from django.urls import reverse
from django.utils.text import slugify
from django.utils.functional import cached_property
from django.db.models.functions import Lower
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from django_auto_one_to_one import AutoOneToOneModel

if getattr(settings, "SITE_PREFIX", ""):
    SITE_PREFIX = "/{}".format(settings.SITE_PREFIX.strip("/"))
else:
    SITE_PREFIX = ""

DATE_FORMAT = "%b %y"

NHS_DIGITAL = "NHS Digital"
VARIOUS = "Various"

DATABASE_NAME_TO_DISPLAY_NAME = dict(
    NHSE_111="NHS 111 Data Set",
    NHSE_IAPT="Improving Access to Psychological Therapies (IAPT) Data Set",
    NHSE_IAPT_PILOT="Improving Access to Psychological Therapies (IAPT) Data Set - pilot",
    NHSE_IAPT_AnnualRefresh="Improving Access to Psychological Therapies (IAPT) Data Set - annual refresh",
    NHSE_Mental_Health="Mental Health Data",
    NHSE_SUSPlus_Live="Secondary Uses Service + (SUS+)",
    NHSE_Reference="NHS England Reference Data"
)

DATABASE_NAME_TO_OWNER = dict(
    NHSE_111=NHS_DIGITAL,
    NHSE_IAPT=NHS_DIGITAL,
    NHSE_IAPT_PILOT=NHS_DIGITAL,
    NHSE_IAPT_AnnualRefresh=NHS_DIGITAL,
    NHSE_Mental_Health=NHS_DIGITAL,
    NHSE_SUSPlus_Live=NHS_DIGITAL,
    NHSE_Reference=VARIOUS
)


def unique_slug(some_cls, name):
    slug = slugify(name)
    if some_cls.objects.filter(slug=slug).exists():
        return "{}{}".format(slug, some_cls.objects.last().id)
    else:
        return slug


class UserProfile(AutoOneToOneModel(User)):
    preview_mode = models.BooleanField(default=False)

    @classmethod
    def get_url_preview_mode_on(cls):
        return SITE_PREFIX + reverse(
            "preview_mode", kwargs=dict(preview_mode=1)
        )

    @classmethod
    def get_url_preview_mode_off(cls):
        return SITE_PREFIX + reverse(
            "preview_mode", kwargs=dict(preview_mode=0)
        )


def turn_preview_mode_off(sender, user, request, **kwargs):
    profile = user.userprofile
    profile.preview_mode = False
    profile.save()

user_logged_out.connect(turn_preview_mode_off)


class NCDRQueryset(models.QuerySet):
    def search(self, search_param):
        """ returns all tables that have columns
        """
        if not search_param:
            return self.none()

        filters = []
        for i in self.model.SEARCH_FIELDS:
            field = "{}__icontains".format(i)
            filters.append(models.Q(**{field: search_param}))
        return self.filter(functools.reduce(operator.or_, filters))


class NcdrModel(models.Model):
    @classmethod
    def get_form_display_template(cls):
        return "forms/display_templates/{}.html".format(
            cls.get_model_api_name()
        )

    @classmethod
    def get_form_description_template(cls):
        return "forms/descriptions/{}.html".format(
            cls.get_model_api_name()
        )

    @classmethod
    def get_form_template(cls):
        return "forms/model_forms/{}.html".format(
            cls.get_model_api_name()
        )

    @classmethod
    def get_model_api_name(cls):
        return cls.__name__.lower()

    @classmethod
    def get_add_url(cls):
        return SITE_PREFIX + reverse(
            "add_many", kwargs=dict(model_name=cls.__name__.lower())
        )

    @classmethod
    def get_search_url(cls):
        return SITE_PREFIX + reverse(
            "search", kwargs=dict(model_name=cls.__name__.lower())
        )

    def get_edit_url(self):
        return SITE_PREFIX + reverse(
            "edit", kwargs=dict(
                pk=self.id,
                model_name=self.__class__.__name__.lower()
            )
        )

    def get_delete_url(self):
        return SITE_PREFIX + reverse(
            "delete", kwargs=dict(
                pk=self.id,
                model_name=self.__class__.__name__.lower()
            )
        )

    def get_display_name(self):
        return self.name

    @classmethod
    def get_model_display_name(cls):
        return cls._meta.verbose_name.title()

    @classmethod
    def get_model_display_name_plural(cls):
        return cls._meta.verbose_name_plural.title()

    @classmethod
    def get_edit_list_url(cls):
        return reverse(
            "edit_list",
            kwargs=dict(model_name=cls.get_model_api_name())
        )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = NCDRQueryset.as_manager()

    class Meta:
        abstract = True


class DatabaseQueryset(NCDRQueryset):
    def all_populated(self, user):
        """ returns all tables that have columns
        """
        return self.filter(
            table__in=Table.objects.all_populated(user)
        ).distinct()


class Database(NcdrModel):
    SEARCH_FIELDS = [
        "name", "display_name", "description", "link"
    ]
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(
        max_length=255, unique=True, blank=True, null=True
    )
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)
    owner = models.CharField(max_length=255, blank=True, null=True)
    objects = DatabaseQueryset.as_manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return SITE_PREFIX + reverse(
            "database_detail", kwargs=dict(db_name=self.name)
        )

    @classmethod
    def get_list_url(self):
        return SITE_PREFIX + reverse(
            "database_list"
        )

    def get_display_name(self):
        if self.display_name:
            return self.display_name
        elif self.name in DATABASE_NAME_TO_DISPLAY_NAME:
            return DATABASE_NAME_TO_DISPLAY_NAME[self.name]
        else:
            return self.name.replace("_", "").title()

    def save(self, *args, **kwargs):
        if not self.owner:
            self.owner = DATABASE_NAME_TO_OWNER.get(self.name)
        return super().save(*args, **kwargs)


class TableQueryset(NCDRQueryset):
    def all_populated(self, user):
        """ returns all tables that have columns
        """
        populated_columns = Column.objects.to_show(user)
        populated_tables = populated_columns.values_list(
            "table_id", flat=True
        ).distinct()
        return Table.objects.filter(
            id__in=populated_tables
        )


class Table(NcdrModel):
    SEARCH_FIELDS = [
        "name", "description", "link"
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)
    is_table = models.BooleanField(
        verbose_name="Table or View",
        choices=((True, 'Table'), (False, 'View'),),
        default=True,
    )

    database = models.ForeignKey(
        Database, on_delete=models.CASCADE
    )

    date_range = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        unique_together = (('name', 'database',),)
        ordering = ['name']

    def __str__(self):
        return self.name

    objects = TableQueryset.as_manager()

    def get_absolute_url(self):
        return SITE_PREFIX + reverse("table_detail", kwargs=dict(
            table_name=self.name,
            db_name=self.database.name
        ))

    def get_display_name(self):
        return "{} / {}".format(self.database.name, self.name)


class Grouping(NcdrModel, models.Model):
    SEARCH_FIELDS = [
        "name", "description"
    ]

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.CharField(
        max_length=255, null=True, blank=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return SITE_PREFIX + reverse("grouping_detail", kwargs=dict(
            slug=self.slug,
        ))

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        return super(Grouping, self).save(*args, **kwargs)


class DataElement(NcdrModel, models.Model):
    SEARCH_FIELDS = [
        "name", "description"
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default="")
    grouping = models.ManyToManyField(
        Grouping, null=True, blank=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ColumnQueryset(NCDRQueryset):
    def to_show(self, user):
        if user.is_authenticated and user.userprofile.preview_mode:
            return self.order_by(Lower('name'))
        else:
            return self.filter(
                published=True
            ).order_by(Lower('name'))

    def unpublished(self):
        return self.filter(published=False)


class Column(NcdrModel, models.Model):
    DATA_TYPE_CHOICES = (
        ("datetime", "datetime",),
        ("date", "date",),
        ("int", "int",),
        ("bigint", "bigint",),
        ("varchar(1)", "varchar(1)",),
        ("varchar(2)", "varchar(2)",),
        ("varchar(3)", "varchar(3)",),
        ("varchar(4)", "varchar(4)",),
        ("varchar(5)", "varchar(5)",),
        ("varchar(6)", "varchar(6)",),
        ("varchar(7)", "varchar(7)",),
        ("varchar(8)", "varchar(8)",),
        ("varchar(9)", "varchar(9)",),
        ("varchar(10)", "varchar(10)",),
        ("varchar(11)", "varchar(11)",),
        ("varchar(12)", "varchar(12)",),
        ("varchar(13)", "varchar(13)",),
        ("varchar(14)", "varchar(14)",),
        ("varchar(15)", "varchar(15)",),
        ("varchar(16)", "varchar(16)",),
        ("varchar(17)", "varchar(17)",),
        ("varchar(18)", "varchar(18)",),
        ("varchar(19)", "varchar(19)",),
        ("varchar(20)", "varchar(20)",),
        ("varchar(50)", "varchar(50)",),
        ("varchar(100)", "varchar(100)",),
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Column"
        unique_together = (("name", "table",),)

    SEARCH_FIELDS = [
        "name", "description"
    ]

    objects = ColumnQueryset.as_manager()

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")
    data_type = models.CharField(max_length=255, choices=DATA_TYPE_CHOICES)
    derivation = models.TextField(blank=True, default="")
    data_element = models.ForeignKey(
        DataElement, on_delete=models.SET_NULL, null=True, blank=True
    )
    table = models.ForeignKey(Table, on_delete=models.CASCADE)

    # currently the below are not being shown in the template
    # after requirements are finalised we could consider removing them.
    technical_check = models.CharField(max_length=255, null=True, blank=True)
    is_derived_item = models.NullBooleanField(
        default=False, verbose_name="Is the item derived?"
    )
    definition_id = models.IntegerField(null=True, blank=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    created_date_ext = models.DateField(blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)
    published = models.BooleanField(default=False)

    @property
    def link_display_name(self):
        if self.link:
            stripped = self.link.lstrip("http://").lstrip("https://")
            return stripped.lstrip("www.").split("/")[0]

    def get_absolute_url(self):
        return SITE_PREFIX + reverse("column_detail", kwargs=dict(
            slug=self.slug,
        ))

    @classmethod
    def get_unpublished_list_url(cls):
        return SITE_PREFIX + reverse("unpublished_list", kwargs=dict(
            model_name=cls.get_model_api_name()
        ))

    @classmethod
    def get_publish_all_url(cls):
        return SITE_PREFIX + reverse("publish_all")

    def get_publish_url(self):
        return SITE_PREFIX + reverse("publish", kwargs=dict(
            pk=self.id, publish=1
        ))

    def get_unpublish_url(self):
        return SITE_PREFIX + reverse("publish", kwargs=dict(
            pk=self.id, publish=0
        ))

    def get_bread_crumb_link(self):
        if self.name[0] in range(10):
            from csv_schema import views
            return SITE_PREFIX + reverse("column_list", kwargs=dict(
                letter=views.ColumnList.NUMERIC
            ))
        return SITE_PREFIX + reverse("column_list", kwargs=dict(
            letter=self.name[0].upper()
        ))

    def get_bread_crumb_name(self):
        if self.name[0] in range(10):
            from csv_schema import views
            return views.ColumnList.NUMERIC
        return self.name[0].upper()

    @cached_property
    def useage_count(self):
        count = self.tables.count()
        if self.data_element:
            count += self.data_element.column_set.count()
        return count

    @cached_property
    def related(self):
        """
            returns a tuple of (table, columns within the table)
            the column names are sorted alphabetically

            the tables are sorted by database name then name
        """
        other_columns = self.data_element.column_set.exclude(id=self.id)
        other_columns = other_columns.order_by(
            "table__name"
        )
        return other_columns.order_by("table__database__name")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self.__class__, self.name)
        return super(Column, self).save(*args, **kwargs)
