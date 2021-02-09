from django.utils.text import slugify

from ncdr.importers import db_api as api

from ..models import DataElement, Grouping


def get_rows():
    query = "select * from vw_Export_Standard_GroupingMapping"
    return api.query(query)


def import_from_db(version):
    rows = get_rows()

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
        ).distinct()
    }

    for row in rows:
        grouping = groupingLUT[row["Grouping"]]
        # data_element = deLUT[row["Data Element"]]

        data_element = data_elementLUT.get(row["Data Element"])
        if data_element:
            data_element.description = row["Data Element Description"]
            data_element.save()

            data_element.grouping.add(grouping)
