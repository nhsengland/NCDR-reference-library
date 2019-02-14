# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.signals import user_logged_out
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify

from ncdr.models import BaseModel, BaseQuerySet

DATE_FORMAT = "%b %y"


def turn_preview_mode_off(sender, user, request, **kwargs):
    user.preview_mode = False
    user.save()


user_logged_out.connect(turn_preview_mode_off)


class DatabaseQueryset(BaseQuerySet):
    def viewable(self, user):
        """Returns all Databases with Schemas that contain viewable Tables."""
        schemas = Schema.objects.filter(tables__in=Table.objects.viewable(user))
        return (
            self.filter(schemas__in=schemas).distinct().order_by(Lower("display_name"))
        )


class Database(BaseModel):
    SEARCH_FIELDS = ["display_name", "name", "description", "link"]
    name = models.CharField(max_length=255, unique=True)
    display_name = models.TextField(blank=True, null=True)
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)
    owner = models.CharField(max_length=255, blank=True, null=True)

    objects = DatabaseQueryset.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("database_detail", kwargs={"db_name": self.name})

    @classmethod
    def get_list_url(self):
        return reverse("database_list")

    def get_display_name(self):
        return self.display_name

    @property
    def tables(self):
        """
        Get tables for this database

        It's common to want the Tables for a Database but the two models are
        separated by a Schema.  This property aims to simply that lookup.
        """
        return Table.objects.filter(schema__database=self)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name.replace("_", "").title()
        return super().save(*args, **kwargs)


class TableQueryset(BaseQuerySet):
    def viewable(self, user):
        if user.is_authenticated and user.preview_mode:
            return self

        populated_columns = Column.objects.viewable(user)
        populated_tables = (
            populated_columns.values_list("table_id", flat=True)
            .distinct()
            .order_by(Lower(""))
        )
        return self.filter(id__in=populated_tables)


class Table(BaseModel):
    SEARCH_FIELDS = ["name", "description", "link"]

    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    link = models.URLField(max_length=500, blank=True, null=True)
    is_table = models.BooleanField(
        verbose_name="Table or View",
        choices=((True, "Table"), (False, "View")),
        default=True,
    )
    date_range = models.CharField(max_length=255, blank=True, default="")

    schema = models.ForeignKey(
        "Schema", on_delete=models.CASCADE, related_name="tables"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "schema"]

    def __str__(self):
        return self.name

    objects = TableQueryset.as_manager()

    def get_absolute_url(self):
        kwargs = {"pk": self.pk, "db_name": self.schema.database.name}
        return reverse("table_detail", kwargs=kwargs)

    def get_display_name(self):
        return "{} / {}".format(self.schema.database.name, self.name)


class GroupingQueryset(BaseQuerySet):
    def viewable(self, user):
        return (
            self.filter(dataelement__in=DataElement.objects.viewable(user))
            .distinct()
            .order_by(Lower("name"))
        )


class Grouping(BaseModel, models.Model):
    SEARCH_FIELDS = ["name", "description"]

    objects = GroupingQueryset.as_manager()
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("grouping_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        return super(Grouping, self).save(*args, **kwargs)


class DataElementQueryset(BaseQuerySet):
    def viewable(self, user):
        if user.is_authenticated and user.preview_mode:
            return self

        populated_columns = Column.objects.viewable(user)
        return self.filter(column__in=populated_columns).distinct()


class DataElement(BaseModel, models.Model):
    SEARCH_FIELDS = ["name", "description"]
    objects = DataElementQueryset.as_manager()

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default="")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    grouping = models.ManyToManyField(Grouping)

    def save(self, *args, **kwargs):
        if self.name and not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("data_element_detail", kwargs={"slug": self.slug})

    def get_description(self):
        if self.description:
            return self.description
        else:
            return self.column_set.first().description

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ColumnQueryset(BaseQuerySet):
    def unpublished(self):
        return self.filter(published=False)

    def published(self):
        return self.filter(published=True)

    def viewable(self, user):
        if user.is_authenticated and user.preview_mode:
            return self.order_by(Lower("name"))
        else:
            return self.filter(published=True).order_by(Lower("name"))

    def to_json(self):
        result = []
        for i in self:
            result.append({"published": i.published, "url": i.get_publish_url()})
        return json.dumps(result)


class Column(BaseModel, models.Model):
    DATA_TYPE_CHOICES = (
        ("datetime", "datetime"),
        ("date", "date"),
        ("int", "int"),
        ("bigint", "bigint"),
        ("varchar(1)", "varchar(1)"),
        ("varchar(2)", "varchar(2)"),
        ("varchar(3)", "varchar(3)"),
        ("varchar(4)", "varchar(4)"),
        ("varchar(5)", "varchar(5)"),
        ("varchar(6)", "varchar(6)"),
        ("varchar(7)", "varchar(7)"),
        ("varchar(8)", "varchar(8)"),
        ("varchar(9)", "varchar(9)"),
        ("varchar(10)", "varchar(10)"),
        ("varchar(11)", "varchar(11)"),
        ("varchar(12)", "varchar(12)"),
        ("varchar(13)", "varchar(13)"),
        ("varchar(14)", "varchar(14)"),
        ("varchar(15)", "varchar(15)"),
        ("varchar(16)", "varchar(16)"),
        ("varchar(17)", "varchar(17)"),
        ("varchar(18)", "varchar(18)"),
        ("varchar(19)", "varchar(19)"),
        ("varchar(20)", "varchar(20)"),
        ("varchar(50)", "varchar(50)"),
        ("varchar(100)", "varchar(100)"),
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Column"
        unique_together = ["name", "table", "data_element", "is_derived_item", "link"]

    SEARCH_FIELDS = ["name", "description"]

    objects = ColumnQueryset.as_manager()

    name = models.CharField(max_length=255)
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
        return reverse("column_detail", kwargs={"pk": self.pk})

    @classmethod
    def get_unpublished_list_url(cls):
        return reverse(
            "unpublished_list", kwargs={"model_name": cls.get_model_api_name()}
        )

    @classmethod
    def get_publish_all_url(cls):
        return reverse("publish_all")

    @classmethod
    def get_edit_list_js_template(cls):
        return "forms/column_form_js.html"

    def get_publish_url(self):
        return reverse("columns-detail", kwargs={"pk": self.id})

    @cached_property
    def useage_count(self):
        count = self.tables.count()
        if self.data_element:
            count += self.data_element.column_set.count()
        return count

    @classmethod
    def get_create_template(cls):
        return "forms/create/column_create.html"

    @cached_property
    def related(self):
        """
            returns a tuple of (table, columns within the table)
            the column names are sorted alphabetically

            the tables are sorted by database name then name
        """
        other_columns = self.data_element.column_set.exclude(id=self.id)
        other_columns = other_columns.order_by("table__name")
        return other_columns.order_by("table__schema__database__name")

    def __str__(self):
        return self.name


class SchemaQueryset(BaseQuerySet):
    def viewable(self, user):
        """Returns all Schemas that have Databases with Columns."""
        return (
            self.filter(table__in=Table.objects.viewable(user))
            .distinct()
            .order_by(Lower("name"))
        )


class Schema(BaseModel, models.Model):
    name = models.TextField()

    database = models.ForeignKey(
        "Database", on_delete=models.CASCADE, related_name="schemas"
    )

    objects = SchemaQueryset.as_manager()

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "database"]

    def __str__(self):
        return self.name
