# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import transaction
import csv
from csv_schema import models


# CSV Columns we use
DATABASE = "Database"
SCHEMA = "Schema"
TABLE = "Table/View"
TABLE_OR_VIEW = "Table or View"
DESCRIPTION = "Description"
LINK = "Link"
DATE_RANGE = "Date_Range"


# CSV Columns we ignore
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
    DATE_RANGE,
    LINK
])

DATABASE_NAME_TO_DISPLAY_NAME = dict(
    NHSE_111="NHS 111 Data Set",
    NHSE_IAPT="Improving Access to Psychological Therapies (IAPT) Data Set",
    NHSE_IAPT_Pilot="Improving Access to Psychological Therapies (IAPT) Data Set - pilot",
    NHSE_IAPT_AnnualRefresh="Improving Access to Psychological Therapies (IAPT) Data Set - annual refresh",
    NHSE_Mental_Health="Mental Health Data",
    NHSE_SUSPlus_Live="Secondary Uses Service + (SUS+)",
    NHSE_Reference="NHS England Reference Data"
)

NHS_DIGITAL = "NHS Digital"
VARIOUS = "Various"

DATABASE_NAME_TO_OWNER = dict(
    NHSE_111=NHS_DIGITAL,
    NHSE_IAPT=NHS_DIGITAL,
    NHSE_IAPT_PILOT=NHS_DIGITAL,
    NHSE_IAPT_AnnualRefresh=NHS_DIGITAL,
    NHSE_Mental_Health=NHS_DIGITAL,
    NHSE_SUSPlus_Live=NHS_DIGITAL,
    NHSE_Reference=VARIOUS
)


NA = "N/A"


def process_row(csv_row):
    if not csv_row[TABLE] or csv_row[TABLE] == NA:
        if csv_row[SCHEMA].strip():
            return
        obj, created = models.Database.objects.get_or_create(
            name=csv_row[DATABASE]
        )
        if created:
            obj.owner = DATABASE_NAME_TO_OWNER.get(
                csv_row[DATABASE], None
            )
            obj.display_name = DATABASE_NAME_TO_DISPLAY_NAME.get(
                csv_row[DATABASE]
            )

            obj.save()
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

        obj.date_range = csv_row[DATE_RANGE]
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
