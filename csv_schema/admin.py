# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.db.models import Q

from csv_schema import models


class IsTechnicalCheckedFilter(admin.SimpleListFilter):

    title = "Those That Have Been Technical Checked"

    parameter_name = "technical_check"

    def lookups(self, request, model_admin):

        return (("yes", "Yes"), ("no", "No"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(technical_check__isnull=False).exclude(
                technical_check=""
            )

        if self.value() == "no":
            return queryset.filter(
                Q(technical_check__isnull=True) | Q(technical_check__exact="")
            )


class DatabaseFilter(admin.SimpleListFilter):
    title = "By Database"

    parameter_name = "database__name"

    def lookups(self, request, model_admin):
        db_names = models.Database.objects.all().values_list("name", flat=True)
        return [(i, i) for i in db_names]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(database__name=value)

        return queryset


@admin.register(models.Column)
class ColumnAdmin(admin.ModelAdmin):
    list_filter = [IsTechnicalCheckedFilter]
    list_display = [
        "name",
        "data_type",
        "get_table_name",
        "get_database_name",
        "author",
        "technical_check",
    ]

    def get_table_name(self, obj):
        return obj.table.name

    get_table_name.short_description = "Table"

    def get_database_name(self, obj):
        return obj.table.database.name

    get_database_name.short_description = "Database"


@admin.register(models.Table)
class TableAdmin(admin.ModelAdmin):
    list_filter = [DatabaseFilter]


admin.site.register(models.Database)
