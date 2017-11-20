# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q
from django.contrib import admin
from csv_schema import models

class IsTechnicalCheckedFilter(admin.SimpleListFilter):

    title = 'Has Been Technical Checked'

    parameter_name = 'technical_check'

    def lookups(self, request, model_admin):

        return (
            ('yes', 'Yes'),
            ('no',  'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(technical_check__isnull=False).exclude(technical_check='')

        if self.value() == 'no':
            return queryset.filter(Q(technical_check__isnull=True) | Q(technical_check__exact=''))


class RowsAdmin(admin.ModelAdmin):
    list_filter = [IsTechnicalCheckedFilter]
    list_display = [
        'data_item',
        'data_type',
        'get_table_name',
        'get_database_name',
        'author',
        'technical_check'
    ]

    def get_table_name(self, obj):
        return obj.table.name

    get_table_name.short_description = "Table"

    def get_database_name(self, obj):
        return obj.table.database.name

    get_database_name.short_description = "Database"


class RowsInline(admin.StackedInline):
    model = models.Row

class TableAdmin(admin.ModelAdmin):
    inlines = [RowsInline,]

admin.site.register(models.Database)
admin.site.register(models.Table, TableAdmin)
admin.site.register(models.Row, RowsAdmin)
admin.site.register(models.SiteDescription)
