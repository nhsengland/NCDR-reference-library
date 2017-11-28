# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import calendar
from django.db import transaction
import datetime
import csv
from csv_schema import models


# CSV Columns we use
DATABASE = "Database"
SCHEMA = "Schema"
TABLE = "Table/View"
TABLE_OR_VIEW = "Table or View"
DESCRIPTION = "Description"
DATE_START = "Data Start"
DATE_END = "Data End"
LINK = "Link"


# CSV Columns we ignore
DATE_RANGE = "Date_Range"
RELEASE_SCHEDULE = "Release shec"
ONLY_HISTORIC = "Only Historic"
PROVISIONAL_SCHEDULE = "Provisional Schedule"
UPDATED_FREQUENCY = "Updated Frequency"

EXPECTED_COLUMN_NAMES = set([
    DATABASE,
    SCHEMA,
    TABLE,
    TABLE_OR_VIEW,
    DESCRIPTION,
    DATE_START,
    DATE_END,
    LINK
])


NA = "N/A"


def get_date_start(some_str):
    """
        takes in a string e.g. Apr-13 returns a date of
        1 April 2013
    """
    if some_str.lower() == "ongoing":
        return
    dt = datetime.datetime.strptime(some_str, "%b-%y")
    return dt.date()


def get_date_end(some_str):
    """
        takes in a string e.g. Api-13 returns a date of
        31 April 2013
    """
    if some_str.lower().strip() == "ongoing":
        return

    dt = datetime.datetime.strptime(some_str, "%b-%y")

    year = dt.year
    month = dt.month
    return datetime.date(
        year, month, calendar.monthrange(year, month)[1]
    )


def process_row(csv_row):
    if not csv_row[TABLE] or csv_row[TABLE] == NA:
        obj, _ = models.Database.objects.get_or_create(
            name=csv_row[DATABASE]
        )
    else:
        obj = models.Table.objects.filter(
            name=csv_row[TABLE], database__name=csv_row[DATABASE]
        ).first()

        if not obj:
            db, _ = models.Database.objects.get_or_create(
                name=csv_row[DATABASE]
            )
            obj = models.Table.objects.create(
                database=db,
                name=csv_row[TABLE]
            )

        obj.date_start = get_date_start(csv_row[DATE_START])
        obj.date_end = get_date_end(csv_row[DATE_END])
        obj.is_table = csv_row[TABLE_OR_VIEW] == "Table"

    obj.description = csv_row[DESCRIPTION] or ""

    obj.link = csv_row.get(LINK)
    obj.save()


def validate_csv_structure(reader, file_name):
    field_names = reader.fieldnames
    field_names = set([i.strip() for i in field_names if i.strip()])
    missing = EXPECTED_COLUMN_NAMES - field_names

    if missing:
        raise ValueError(
            'missing fields %s in %s' % (", ".join(missing), file_name)
        )


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
