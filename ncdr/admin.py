from django.contrib import admin

from .models import Column, Database, DataElement, Grouping, Schema, Table, Version


class DatabaseFilter(admin.SimpleListFilter):
    title = "By Database"

    parameter_name = "database__name"

    def lookups(self, request, model_admin):
        db_names = Database.objects.all().values_list("name", flat=True)
        return [(i, i) for i in db_names]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(database__name=value)

        return queryset


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "data_type",
        "get_table_name",
        "get_database_name",
        "author",
    ]

    def get_table_name(self, obj):
        return obj.table.name

    get_table_name.short_description = "Table"

    def get_database_name(self, obj):
        return obj.table.schema.database.name

    get_database_name.short_description = "Database"


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_filter = ["version"]


@admin.register(DataElement)
class DataElementAdmin(admin.ModelAdmin):
    list_filter = ["column__table__schema__database__version"]


@admin.register(Grouping)
class GroupingAdmin(admin.ModelAdmin):
    list_filter = ["dataelement__column__table__schema__database__version"]


@admin.register(Schema)
class SchemaAdmin(admin.ModelAdmin):
    list_filter = ["database__version"]


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_filter = ["schema__database__version", DatabaseFilter]


admin.site.register(Version)
