# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import defaultdict
from django.urls import reverse
from django.db.models import Count
from django.utils.text import slugify
from django.utils.functional import cached_property
from django.db.models.functions import Lower
from django.conf import settings
from django.db import models


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


class AbstractTimeStamped(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DatabaseQueryset(models.QuerySet):
    def all_populated(self):
        """ returns all tables that have columns
        """
        return self.filter(table__in=Table.objects.all_populated()).distinct()


class Database(AbstractTimeStamped):

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)

    objects = DatabaseQueryset.as_manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return SITE_PREFIX + reverse(
            "database_detail", kwargs=dict(db_name=self.name)
        )

    def get_display_name(self):
        display_name = DATABASE_NAME_TO_DISPLAY_NAME.get(self.name)
        if display_name:
            return display_name
        else:
            return self.name.replace("_", "").title()

    def get_owner(self):
        owner = DATABASE_NAME_TO_OWNER.get(self.name)
        if owner:
            return owner


class TableQueryset(models.QuerySet):
    def all_populated(self):
        """ returns all tables that have columns
        """
        return self.annotate(
            column_count=Count('column')
        ).filter(
            column_count__gt=0
        )


class Table(AbstractTimeStamped):
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)
    is_table = models.BooleanField(default=True)
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


class Mapping(AbstractTimeStamped, models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Grouping(AbstractTimeStamped, models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    @property
    def mappings(self):
        return Mapping.objects.filter(
            column__in=self.column_set.all()
        ).distinct().order_by('name')

    def get_absolute_url(self):
        return SITE_PREFIX + reverse("grouping_detail", kwargs=dict(
            slug=self.slug,
        ))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self.__class__, self.name)
        return super(Grouping, self).save(*args, **kwargs)


class ColumnManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        queryset = super(ColumnManager, self).get_queryset(*args, **kwargs)
        return queryset.annotate(
            name_lower=Lower('name'),
        ).order_by('name_lower')


class Column(AbstractTimeStamped, models.Model):
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
        ("varchar(11)", "varchar(1)1",),
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

    objects = ColumnManager()

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="")
    data_type = models.CharField(max_length=255, choices=DATA_TYPE_CHOICES)
    derivation = models.TextField(blank=True, default="")
    tables = models.ManyToManyField(Table)
    mapping = models.ForeignKey(
        Mapping, on_delete=models.SET_NULL, null=True, blank=True
    )

    grouping = models.ForeignKey(
        Grouping, on_delete=models.SET_NULL, null=True, blank=True
    )

    # currently the below are not being shown in the template
    # after requirements are finalised we could consider removing them.
    technical_check = models.CharField(max_length=255, null=True, blank=True)
    is_derived_item = models.NullBooleanField(default=False)
    definition_id = models.IntegerField(null=True, blank=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    created_date_ext = models.DateField(blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    @property
    def link_display_name(self):
        if self.link:
            stripped = self.link.lstrip("http://").lstrip("https://")
            return stripped.lstrip("www.").split("/")[0]

    def get_absolute_url(self):
        return SITE_PREFIX + reverse("column_detail", kwargs=dict(
            slug=self.slug,
        ))

    def get_bread_crumb_link(self):
        if self.name[0] in range(10):
            from csv_schema import views
            return SITE_PREFIX + reverse("ncdr_reference_list", kwargs=dict(
                letter=views.NcdrReferenceList.NUMERIC
            ))
        return SITE_PREFIX + reverse("ncdr_reference_list", kwargs=dict(
            letter=self.name[0].upper()
        ))

    def get_bread_crumb_name(self):
        if self.name[0] in range(10):
            from csv_schema import views
            return views.NcdrReferenceList.NUMERIC
        return self.name[0].upper()

    @cached_property
    def useage_count(self):
        count = self.tables.count()
        if self.mapping:
            count += self.mapping.column_set.count()
        return count

    @cached_property
    def related(self):
        """ returns a tuple of (table, columns_and_mappings_within_the_table)
            the column names are sorted alphabetically

            the tables are sorted by database name then name
        """
        result = []
        result.extend(Column.objects.filter(tables__in=self.tables.all()))
        table_to_columns = defaultdict(list)
        for table in self.tables.all():
            table_to_columns[table].append(self)

        if self.mapping:
            column_set = self.mapping.column_set.exclude(id=self.id)
            for column in column_set:
                for table in column.tables.all():
                    table_to_columns[table].append(column)
            for i, v in table_to_columns.items():
                table_to_columns[i] = sorted(
                    table_to_columns[i], key=lambda x: x.name
                )

        result = [(i, v,) for i, v in table_to_columns.items()]
        result = sorted(result, key=lambda x: x[0].name)
        result = sorted(result, key=lambda x: x[0].database.name)
        return result

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self.__class__, self.name)
        return super(Column, self).save(*args, **kwargs)
