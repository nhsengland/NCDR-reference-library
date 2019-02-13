import csv

from django.db import transaction

from csv_schema.models import DataElement, Grouping


@transaction.atomic
def load_file(file_name):
    with open(file_name, "r", encoding="Windows-1252") as f:
        f.readline()  # ignore the first line since it's blank
        rows = list(csv.DictReader(f, delimiter="¬"))

    for row in rows:
        grouping, _ = Grouping.objects.get_or_create(
            name=row["Grouping"], defaults={"description": row["Grouping Description"]}
        )

        data_element, _ = DataElement.objects.get_or_create(
            name=row["Data Element"],
            defaults={"description": row["Data Element Description"]},
        )

        data_element.grouping.add(grouping)
