import json

from django import forms
from django.db import transaction

from .models import ColumnImage, Version


class UploadForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ["db_structure", "definitions", "grouping_mapping"]


class ColumnImageForm(forms.ModelForm):
    def get_selected_json(self):
        result = []
        if self.instance:
            for relation in self.instance.columnimagerelation_set.all():
                path = [
                    relation.database_name,
                    relation.schema_name,
                    relation.table_name,
                ]
                column_path = path + [relation.column_name]
                result.append(
                    {
                        "id": json.dumps(column_path),
                        "text": relation.column_name,
                        "group": ".".join(path),
                    }
                )
        return result

    class Meta:
        model = ColumnImage
        fields = ["image"]

    @transaction.atomic
    def save(self, *args, **kwargs):
        save_result = super().save(*args, **kwargs)
        relations = []
        for column_path_json in self.data.getlist("relation"):
            db_name, schema_name, table_name, column_name = json.loads(column_path_json)
            relation, _ = self.instance.columnimagerelation_set.get_or_create(
                database_name=db_name,
                schema_name=schema_name,
                table_name=table_name,
                column_name=column_name,
            )
            relations.append(relation)

        self.instance.columnimagerelation_set.exclude(
            id__in=[i.id for i in relations]
        ).delete()
        return save_result
