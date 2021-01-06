from django import forms
from django.db import transaction

from .models import Column, ColumnImage, Version


class UploadForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ["db_structure", "definitions", "grouping_mapping"]


def get_column_choices():
    columns = Column.objects.filter(
        table__schema__database__version__is_published=True
    ).values_list("id", flat=True)
    return [(i, i) for i in columns]


class ColumnImageForm(forms.ModelForm):
    relation = forms.MultipleChoiceField(choices=get_column_choices)

    def get_selected_json(self):
        result = []
        if self.instance:
            for relation in self.instance.columnimagerelation_set.all():
                column = Column.objects.filter(
                    name=relation.column_name,
                    table__name=relation.table_name,
                    table__schema__name=relation.schema_name,
                    table__schema__database__name=relation.database_name,
                ).first()
                if column:
                    table = column.table
                    schema = table.schema
                    database = schema.database
                    result.append(
                        {
                            "id": column.id,
                            "text": column.name,
                            "group": f"{database.name}.{schema.name}.{table.name}",
                        }
                    )
        return result

    class Meta:
        model = ColumnImage
        fields = ["image", "relation"]

    @transaction.atomic
    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)

        column_ids = [int(i) for i in self.data.getlist("relation")]
        columns = Column.objects.filter(id__in=column_ids).select_related(
            "table", "table__schema", "table__schema__database"
        )
        for column in columns:
            table = column.table
            schema = table.schema
            db = schema.database
            self.instance.columnimagerelation_set.get_or_create(
                database_name=db.name,
                schema_name=schema.name,
                table_name=table.name,
                column_name=column.name,
            )
        return result
