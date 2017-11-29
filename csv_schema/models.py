# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.core.urlresolvers import reverse
from django.db.models import Count

from django.db import models
DATE_FORMAT = "%b %y"


class AbstractTimeStamped(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Database(AbstractTimeStamped):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("database_detail", kwargs=dict(db_name=self.name))


class TableQueryset(models.QuerySet):
    def all_populated(self):
        """ returns all tables that have columns
        """
        return self.annotate(
            column_count=Count('column')
        ).filter(
            column_count__gt=0
        )


@python_2_unicode_compatible
class Table(AbstractTimeStamped):
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)
    is_table = models.BooleanField(default=True)
    database = models.ForeignKey(
        Database, on_delete=models.CASCADE
    )

    # brought in as Apr-2015 but we translate that to, for example 1 April 2015
    # because when we want this actually entered, that's the kind of data we want
    date_start = models.DateField(blank=True, null=True)


    # brought in as Apr-2015 but we translate that to, for example 31 April 2015
    # because when we want this actually entered, that's the kind of data we want
    date_end = models.DateField(blank=True, null=True)

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

    @property
    def start(self):
        if self.date_start:
            return self.date_start.strftime(DATE_FORMAT)

    @property
    def end(self):
        if self.date_end:
            return self.date_end.strftime(DATE_FORMAT)


@python_2_unicode_compatible
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
        unique_together = (('table', 'data_item',),)
        ordering = ['table', 'data_item']

    data_item = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    data_type = models.CharField(max_length=255, choices=DATA_TYPE_CHOICES)
    derivation = models.TextField(blank=True, default="")
    table = models.ForeignKey(
        Table, on_delete=models.CASCADE
    )

    # currently the below are not being shown in the template
    # after requirements are finalised we could consider removing them.
    technical_check = models.CharField(max_length=255, null=True, blank=True)
    is_derived_item = models.NullBooleanField(default=False)
    definition_id = models.IntegerField(null=True, blank=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    created_date_ext = models.DateField(blank=True, null=True)

    def __str__(self):
        return "{} ({}.{})".format(
            self.data_item,
            self.table.name,
            self.table.database.name
        )


@python_2_unicode_compatible
class DataDictionaryReference(AbstractTimeStamped):
    name = models.CharField(max_length=255)
    link = models.URLField(max_length=500, blank=True, null=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('column', 'name',),)
        ordering = ['name']

    def __str__(self):
        return "{} ({}.{})".format(
            self.name,
            self.link,
            self.column
        )


class SiteDescription(models.Model):
    description = models.TextField()
