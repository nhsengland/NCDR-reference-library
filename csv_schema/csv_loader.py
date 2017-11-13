# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import transaction
import datetime
import csv
from csv_schema import models

TABLE_NAME = "Table"
DATABASE = "Database"
CREATED_DATE = "Created_Date"

# the name of the row as it comes in from the csv
DATA_DICTIONARY_NAME = "Data Dictionary Name"
DATA_DICTIONARY_LINKS = "Data Dictionary Links"
IS_DERIVED_ITEM = "Is_Derived_Item"
DATA_ITEM_NAME = "Data Item"
DATA_DICTIONARY_DESCRIPTION = "Description"
DERIVATION_METHODOLOGY = "Derivation_Methodology"
DATA_TYPE = "Data type"
DEFINITION_ID = "Definition ID"
TECHNICAL_CHECK = "Technical check"
BUSINESS_CHECK = "Business check"
RK_2 = "RK 2"
SCHEMA = "Schema"
CHECKED = "Checked"


# These are the minimum expected csv columns, if they're missing, blow up
EXPECTED_ROW_NAMES = set([
    DATABASE,
    TABLE_NAME,
    DATA_ITEM_NAME,
    DATA_DICTIONARY_DESCRIPTION,
    DATA_TYPE,
    IS_DERIVED_ITEM,
    DERIVATION_METHODOLOGY,
    DATA_DICTIONARY_NAME,
    DATA_DICTIONARY_LINKS,
    "Data Dictionary Links",
])

CSV_FIELD_TO_ROW_FIELD = {
    DEFINITION_ID: "definition_id",
    DATA_ITEM_NAME: "data_item",
    DATA_DICTIONARY_DESCRIPTION: "description",
    DATA_TYPE: "data_type",
    IS_DERIVED_ITEM: "is_derived_item",
    DERIVATION_METHODOLOGY: "derivation",
    TECHNICAL_CHECK: "technical_check",
    "Author": "author",
    "Created_Date": "created_date_ext"
}

IGNORED_FIELDS = set([
    BUSINESS_CHECK,
    RK_2,
    SCHEMA,
    CHECKED
])


def process_is_derived(value):
    if not value:
        # don't try and save an empty string
        value = None
    elif value.lower() not in [u"yes", u"no"]:
        raise ValueError(
            "Unable to recognise is derived item {}".format(
                value
            )
        )
    else:
        value = value.lower() == u"yes"

    return value


def process_created_date(value):
    if not value:
        return None
    else:
        return datetime.datetime.strptime(value, "%d/%m/%Y").date()


def process_data_dictionary_reference(db_row, csv_row):
    """ we store data dictionary links and names as a seperate foreign key table
        we want there to be one link to one name after being split by new lines

        this is not always the case.

        work arounds.

        (i) if there is only a single link and lots of names, apply that link
            to all the names

        (ii) if there are no links, just save a name
    """
    names_str = csv_row[DATA_DICTIONARY_NAME]
    if names_str == "N//A" or names_str == "N/A":
        db_row.datadictionaryreference_set.all().delete()
        return

    links_str = csv_row[DATA_DICTIONARY_LINKS]
    names = [i.strip() for i in names_str.split("\n") if i.strip()]
    links = [i.strip() for i in links_str.split("\n") if i.strip()]
    if not len(names) == len(links):
        if not names:
            raise ValueError(
                'found links but no names for {}.{}.{}'.format(
                    db_row.table.database.name,
                    db_row.table.name,
                    db_row.data_item
                )
            )
        elif len(links) == 1:
            links = [links[0] for i in range(len(names))]
        elif not links:
            links = [None for i in range(len(names))]
        else:
            raise ValueError(
                'for {}.{}.{} the number of links is different'.format(
                    db_row.table.database.name,
                    db_row.table.name,
                    db_row.data_item
                )
            )

    obj_args = [dict(name=i[0], link=i[1]) for i in zip(names, links)]

    existing = []
    new_db_refs = []
    for obj_arg in obj_args:
        existing_row = db_row.datadictionaryreference_set.filter(
            **obj_arg
        ).first()

        if existing_row:
            existing.append(existing_row)
        else:
            new_db_refs.append(obj_arg)

    db_row.datadictionaryreference_set.exclude(
        id__in=[i.id for i in existing]
    ).delete()

    for new_db_ref in new_db_refs:
        db_row.datadictionaryreference_set.create(**new_db_ref)


def clean_value(some_field):
    return unicode(some_field, 'utf-8').strip()


def process_row(csv_row, file_name):
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

    known_fields = EXPECTED_ROW_NAMES.union(CSV_FIELD_TO_ROW_FIELD.keys())
    for field_name in field_names:
        value = clean_value(csv_row[field_name])
        field_name = field_name.strip()

        if field_name == TABLE_NAME or field_name == DATABASE:
            # these fields are the Foreign keys handled above.
            continue

        if isinstance(value, str):
            value = value.strip()

        if field_name in IGNORED_FIELDS:
            continue

        if value and field_name not in known_fields:
            e = "We are not saving a value for {} in {}, should we be?"
            raise ValueError(
                e.format(field_name, file_name)
            )
        elif not value and field_name not in CSV_FIELD_TO_ROW_FIELD:
            continue

        # these are compounded into a foreign key, so we
        # deal with these later
        if field_name in [DATA_DICTIONARY_NAME, DATA_DICTIONARY_LINKS]:
            continue

        db_column_name = CSV_FIELD_TO_ROW_FIELD[field_name]
        if field_name == IS_DERIVED_ITEM:
            value = process_is_derived(value)

        if field_name == CREATED_DATE:
            value = process_created_date(value)

        # don't accidentally put an empty space where a None should be
        if field_name == DEFINITION_ID:
            if value == '':
                value = None

        setattr(row, db_column_name, value)
    try:
        row.save()
    except:
        raise
    process_data_dictionary_reference(row, csv_row)


def validate_csv_structure(reader, file_name):
    field_names = reader.fieldnames
    field_names = set([i.strip() for i in field_names if i.strip()])
    missing = EXPECTED_ROW_NAMES - field_names

    if missing:
        raise ValueError(
            'missing fields %s in %s' % (", ".join(missing), file_name)
        )


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
        validate_csv_structure(reader, file_name)

        for csv_row in reader:
            process_row(csv_row, file_name)
