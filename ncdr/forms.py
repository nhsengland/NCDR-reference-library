import json

from django import forms
from django.db import transaction

from .models import ColumnImage, Database, Table, Version


class UploadForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ["db_structure", "definitions", "grouping_mapping"]


def get_column_choices_qs():
    """
    Takes in a column queryset
    Filters it so it only includes published columns
    Returns a list of tuples of
    [{db.name}, {schema.name}, {table.name}, {col.name}]

    We build a db lookup list first to save a thousand
    preselect queries for what is only 1 of ~6.
    """
    databases = Database.objects.filter(version__is_published=True)

    database_id_lut = {i.id: i.name for i in databases}

    tables = (
        Table.objects.filter(schema__database__id__in=database_id_lut.keys())
        .prefetch_related("column_set")
        .select_related("schema")
    )

    result = []
    for table in tables:
        for column in table.column_set.all():
            db_id = table.schema.database_id
            db_name = database_id_lut[db_id]
            schema_name = table.schema.name
            result.append((db_name, schema_name, table.name, column.name))

    return result


def column_choices():
    result = [(json.dumps(i), ".".join(i)) for i in get_column_choices_qs()]
    return sorted(result, key=lambda x: len(x[0]), reverse=True)


class ColumnImageForm(forms.ModelForm):
    relation = forms.MultipleChoiceField(choices=column_choices)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        initial = kwargs.pop("initial", None)
        if instance:
            initial_relation = []

            for relation in instance.columnimagerelation_set.all():
                if Database.objects.filter(
                    version__is_published=True,
                    name=relation.database_name,
                    schemas__name=relation.schema_name,
                    schemas__tables__name=relation.table_name,
                    schemas__tables__column__name=relation.column_name,
                ).exists():
                    initial_relation.append(
                        json.dumps(
                            [
                                relation.database_name,
                                relation.schema_name,
                                relation.table_name,
                                relation.column_name,
                            ]
                        )
                    )

            if initial:
                initial["relation"] = initial_relation
            else:
                initial = {"relation": initial_relation}

        return super().__init__(*args, initial=initial, **kwargs)

    class Meta:
        model = ColumnImage
        fields = ["image", "relation"]

    @transaction.atomic
    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        relation_strings = self.data.getlist("relation")
        for relation_string in relation_strings:
            [db_name, schema_name, table_name, column_name] = json.loads(
                relation_string
            )
            self.instance.columnimagerelation_set.get_or_create(
                database_name=db_name,
                schema_name=schema_name,
                table_name=table_name,
                column_name=column_name,
            )
        return result
