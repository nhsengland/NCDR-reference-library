import csv

from ..models import DataElement, Grouping


def load_file(fd, version):
    fd.readline()  # ignore the first line since it's blank
    rows = list(csv.DictReader(fd, delimiter="¬"))

    existing_names = set(Grouping.objects.values_list("name", flat=True))
    csv_desc_by_name = {row["Grouping"]: row["Grouping Description"] for row in rows}
    missing_names = set(csv_desc_by_name.keys()) - set(existing_names)
    Grouping.objects.bulk_create(
        Grouping(name=name, description=csv_desc_by_name[name])
        for name in missing_names
    )
    groupingLUT = {g.name: g for g in Grouping.objects.all()}

    data_elementLUT = {de.name: de for de in DataElement.objects.all()}

    for row in rows:
        grouping = groupingLUT[row["Grouping"]]
        # data_element = deLUT[row["Data Element"]]

        data_element = data_elementLUT[row["Data Element"]]
        if not data_element.description:
            data_element.description = row["Data Element Description"]
            data_element.save()

        data_element.grouping.add(grouping)
