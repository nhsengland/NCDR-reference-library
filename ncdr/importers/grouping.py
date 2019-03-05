import csv

from ..models import DataElement, Grouping


def load_file(fd, version):
    fd.readline()  # ignore the first line since it's blank
    rows = list(csv.DictReader(fd, delimiter="¬"))

    for row in rows:
        grouping, _ = Grouping.objects.get_or_create(
            name=row["Grouping"], defaults={"description": row["Grouping Description"]}
        )

        data_element, _ = DataElement.objects.get_or_create(
            name=row["Data Element"],
            defaults={"description": row["Data Element Description"]},
        )

        data_element.grouping.add(grouping)
