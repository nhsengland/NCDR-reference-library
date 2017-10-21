# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models


class AbstractTimeStamped(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Database(AbstractTimeStamped):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Table(AbstractTimeStamped):
    name = models.CharField(max_length=255)
    database = models.ForeignKey(Database)

    class Meta:
        unique_together = (('name', 'database',),)
        ordering = ['name']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Row(AbstractTimeStamped):
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
        unique_together = (('table', 'data_dictionary_name',),)
        ordering = ['table', 'data_item']

    definition_id = models.IntegerField(null=True, blank=True)
    data_item = models.CharField(max_length=255)
    description = models.TextField()
    data_type = models.CharField(max_length=255, choices=DATA_TYPE_CHOICES)
    is_derived_item = models.BooleanField(default=False)

    derivation = models.TextField()
    data_dictionary_name = models.CharField(max_length=255)
    data_dictionary_link = models.URLField(max_length=500)
    table = models.ForeignKey(Table)
    technical_check = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{} ({}.{})".format(
            self.data_dictionary_name,
            self.table.name,
            self.table.database.name
        )


class SiteDescription(models.Model):
    description = models.TextField()
