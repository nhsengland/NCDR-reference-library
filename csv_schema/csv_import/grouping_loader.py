import csv
from django.db import transaction
from csv_schema import models

EXPECTED_COLUMN_NAMES = [
    "Group name",
    "Group description",
    "Mapping 1"
]


def process_row(row):

    # skip it if its an empty row
    if not any(row.values()):
        return

    grouping, _ = models.Grouping.objects.get_or_create(
        name=row["Group name"]
    )
    grouping.description = row["Group description"]

    for field in row.keys():
        # now just add the mappings
        if not field.startswith("Mapping "):
            continue
        if row[field]:
            data_element, _ = models.DataElement.objects.get_or_create(
                name=row[field]
            )
            grouping.dataelement_set.add(data_element)
    grouping.save()


def validate_csv_structure(reader, file_name):
    field_names = reader.fieldnames
    missing = set(EXPECTED_COLUMN_NAMES) - set(field_names)
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
