# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse
from django.db.models import Count
from django.utils.text import slugify

from django.db import models
DATE_FORMAT = "%b %y"

DATABASE_NAME_TO_DISPLAY_NAME = dict(
    NHSE_111="NHS 111 Minimum Data Set",
    NHSE_IAPT="Improving Access to Psychological Therapies Data Set",
    NHSE_IAPT_PILOT="Improving Access to Psychological Therapies Data Set Pilot",
    NHSE_Mental_Health="Mental Health Services Data Set",
    NHSE_SUSPlus_Live="Secondary Uses Service Plus (SUS+)"
)


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
        return reverse("database_detail", kwargs=dict(db_name=self.name))

    def get_display_name(self):
        display_name = DATABASE_NAME_TO_DISPLAY_NAME.get(self.name)
        if display_name:
            return display_name
        else:
            return display_name.replace("_", "")


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
        return reverse("table_detail", kwargs=dict(
            table_name=self.name,
            db_name=self.database.name
        ))

    def get_display_name(self):
        return "Database: {} - Table: {}".format(self.database.name, self.name)


class Mapping(AbstractTimeStamped, models.Model):
    name = models.CharField(max_length=255, unique=True)


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

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="")
    data_type = models.CharField(max_length=255, choices=DATA_TYPE_CHOICES)
    derivation = models.TextField(blank=True, default="")
    tables = models.ManyToManyField(Table)
    mapping = models.ForeignKey(
        Mapping, on_delete=models.SET_NULL, null=True, blank=True
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
        return reverse("column_detail", kwargs=dict(
            slug=self.slug,
        ))

    def get_bread_crumb_link(self):
        if self.name[0] in range(10):
            from csv_schema import views
            return reverse("ncdr_reference_list", kwargs=dict(
                letter=views.NcdrReferenceList.NUMERIC
            ))
        return reverse("ncdr_reference_list", kwargs=dict(
            letter=self.name[0].upper()
        ))

    def get_bread_crumb_name(self):
        if self.name[0] in range(10):
            from csv_schema import views
            return views.NcdrReferenceList.NUMERIC
        return self.name[0].upper()

    @property
    def other_references(self):
        return self.link or self.tables.count() > 1

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Column, self).save(*args, **kwargs)


class SiteDescription(models.Model):
    description = models.TextField()
