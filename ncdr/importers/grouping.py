import csv

from django.utils.text import slugify

from ..models import DataElement, Grouping


def load_file(fd, version):
    rows = list(csv.DictReader(fd, delimiter="¬"))

    csv_desc_by_name = {row["Grouping"]: row["Grouping Description"] for row in rows}
    groupings = Grouping.objects.bulk_create(
        Grouping(name=name, slug=slugify(name), description=description)
        for name, description in csv_desc_by_name.items()
    )
    groupingLUT = {g.name: g for g in groupings}

    data_elementLUT = {
        de.name: de
        for de in DataElement.objects.filter(
            column__table__schema__database__version=version
        )
    }

    for row in rows:
        grouping = groupingLUT[row["Grouping"]]
        # data_element = deLUT[row["Data Element"]]

        data_element = data_elementLUT.get(row["Data Element"])
        if data_element:
            data_element.description = row["Data Element Description"]
            data_element.save()

            data_element.grouping.add(grouping)
