# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

from django.db import transaction

from csv_schema import models


def validate_csv_structure(reader, file_name):
    field_names = reader.fieldnames
    field_names = set([i.strip() for i in field_names if i.strip()])
    EXPECTED_COLUMN_NAMES = set(["Mapping", "Item_Name", "Group"])
    missing = EXPECTED_COLUMN_NAMES - field_names

    if missing:
        raise ValueError(
            'missing fields %s in %s' % (", ".join(missing), file_name)
        )


def process_row(csv_row):
    if not csv_row.get("Item_Name") and not csv_row.get("Mapping"):
        return
    item_name = csv_row["Item_Name"]
    column = models.Column.objects.get(name=item_name)
    mapping, _ = models.Mapping.objects.get_or_create(name=csv_row["Mapping"])
    mapping.column_set.add(column)

    grouping, _ = models.Grouping.objects.get_or_create(name=csv_row["Group"])
    grouping.column_set.add(column)


@transaction.atomic
def load_file(file_name):
    """ loads in a file containing all the information about tables
        and databases
    """
    with open(file_name) as csv_file:
        reader = csv.DictReader(csv_file)
        validate_csv_structure(reader, file_name)

        for csv_row in reader:
            process_row(csv_row)
