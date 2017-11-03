# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
import datetime
import csv
from csv_schema import models

TABLE_NAME = "Table_Name"
DATABASE = "Database"
CREATED_DATE = "Created_Date"

# the name of the row as it comes in from the csv
DATA_DICTIONARY_NAME = "Data Dictionary Name"
DATA_DICTIONARY_LINKS = "Data Dictionary Links"
IS_DERIVED_ITEM = "Is_Derived_Item"
DATA_ITEM_NAME = "Data_Item_Name"


# These are the minimum expected csv columns, if they're missing, blow up
EXPECTED_ROW_NAMES = set([
    DATABASE,
    TABLE_NAME,
    DATA_ITEM_NAME,
    "Data_Item_Description",
    "Data_Type",
    IS_DERIVED_ITEM,
    "Derivation_Methodology",
    DATA_DICTIONARY_NAME,
    DATA_DICTIONARY_LINKS,
    "Data Dictionary Links",
])

CSV_FIELD_TO_ROW_FIELD = {
    "Definition ID": "definition_id",
    DATA_ITEM_NAME: "data_item",
    "Data_Item_Description": "description",
    "Data_Type": "data_type",
    IS_DERIVED_ITEM: "is_derived_item",
    "Derivation_Methodology": "derivation",
    "Technical check": "technical_check",
    "Author": "author",
    "Created_Date": "created_date_ext"
}


def process_is_derived(value):
    if not value:
        # don't try and save an empty string
        value = None
    elif value.lower() not in ["yes", "no"]:
        raise ValueError(
            "Unable to recognise is derived item {}".format(
                value
            )
        )
    else:
        value = value.lower() == "yes"

    return value


def process_created_date(value):
    if not value:
        return None
    else:
        return datetime.datetime.strptime(value, "%d/%m/%Y").date()


def process_data_dictionary_reference(db_row, csv_row):
    names_str = getattr(csv_row, DATA_DICTIONARY_NAME)
    links_str = getattr(csv_row, DATA_DICTIONARY_LINKS)
    names = names_str.split("\n")
    links = links_str.split("\n")
    if len(names) !== len(links):
        raise ValueError('for {}.{}.{} the number of links is different')


def process_row(csv_row):
    if not any(i for i in csv_row.values() if i.strip()):
        # if its an empty row, skip it
            return

    db, _ = models.Database.objects.get_or_create(
        name=csv_row[DATABASE]
    )
    table, _ = models.Table.objects.get_or_create(
        name=csv_row[TABLE_NAME],
        database=db
    )
    row, _ = models.Row.objects.get_or_create(
        table=table,
        data_item=csv_row[DATA_ITEM_NAME]
    )
    field_names = csv_row.keys()

    for field_name in field_names:
        if field_name == TABLE_NAME or field_name == DATABASE:
            # these fields are the Foreign keys handled above.
            continue
        value = csv_row[field_name]

        if isinstance(value, str):
            value = value.strip()

        if value and field_name not in CSV_FIELD_TO_ROW_FIELD:
            e = "We are not saving a value for {}, should we be?"
            raise ValueError(
                e.format(field_name)
            )
        elif not value and field_name not in CSV_FIELD_TO_ROW_FIELD:
            continue

        db_column_name = CSV_FIELD_TO_ROW_FIELD[field_name]
        if field_name == IS_DERIVED_ITEM:
            value = process_is_derived(value)

        if field_name == CREATED_DATE:
            value = process_created_date(value)

        if isinstance(value, str):
            # replace non asci characters with spaces
            value = ''.join(i if ord(i) < 128 else ' ' for i in value)
        setattr(row, db_column_name, value)
    row.save()
    process_data_dictionary_reference(row, csv_row)


def validate_csv_structure(reader):
    field_names = reader.fieldnames
    field_names = set([i for i in field_names if i.strip()])
    missing = EXPECTED_ROW_NAMES - field_names

    if missing:
        raise ValueError('missing fields %s' % ", ".join(missing))


@transaction.atomic
def load_file(file_name):
    """ loads in a file. At present the columns are a bit in flux so our
        methodolgy is:

        1. if there's a column that's populated but not in our database model
           blow up

        2. if there's a column that's not in our database model, but also
           not populated, ignore it
    """
    with open(file_name) as csv_file:
        reader = csv.DictReader(csv_file)
        validate_csv_structure(reader)

        for csv_row in reader:
            process_row(csv_row)
