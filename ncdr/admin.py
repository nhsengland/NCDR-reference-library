from django.contrib import admin

from .models import Column, Database, Table


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
        return obj.table.database.name

    get_database_name.short_description = "Database"


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_filter = [DatabaseFilter]


admin.site.register(Database)
