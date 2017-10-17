# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
import csv
from csv_schema import models

EXPECTED_ROW_NAMES = set([
    "Definition ID",
    "Database",
    "Table",
    "Data Item",
    "Description",
    "Data type",
    "Is_Derived_Item",
    "Derivation_Methodology",
    "Data Dictionary Name",
    "Data Dictionary Links",
    "Technical check"
])

CSV_FIELD_TO_ROW_FIELD = {
    "Definition ID": "definition_id",
    "Data Item": "data_item",
    "Description": "description",
    "Data type": "data_type",
    "Is_Derived_Item": "is_derived_item",
    "Derivation_Methodology": "derivation",
    "Data Dictionary Name": "data_dictionary_name",
    "Data Dictionary Links": "data_dictionary_link",
    "Technical check": "technical_check"
}


@transaction.atomic
def load_file(file_name):
    with open(file_name) as csv_file:
        reader = csv.DictReader(csv_file)
        field_names = reader.fieldnames
        field_names = set([i for i in field_names if i.strip()])
        unexpected = field_names - EXPECTED_ROW_NAMES
        missing = EXPECTED_ROW_NAMES - field_names
        if unexpected:
            raise ValueError('unexpected fields %s' % unexpected)
        if missing:
            raise ValueError('missing_fields fields %s' % missing)
        for csv_row in reader:
            db, _ = models.Database.objects.get_or_create(
                name=csv_row["Database"]
            )
            table, _ = models.Table.objects.get_or_create(
                name=csv_row["Table"],
                database=db
            )
            row, _ = models.Row.objects.get_or_create(
                table=table,
                data_dictionary_name=csv_row["Data Dictionary Name"]
            )

            for k, v in CSV_FIELD_TO_ROW_FIELD.items():
                value = csv_row[k]
                if k == "Is_Derived_Item":
                    if value.lower() not in ["yes", "no"]:
                        raise ValueError(
                            "Unable to recognise derived item {}".format(
                                value
                            )
                        )

                    value = k.lower() == "yes"
                setattr(row, v, value)

            row.save()
