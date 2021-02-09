import collections

from django.utils.text import slugify

from ncdr.importers import db_api as api

from ..models import Column, DataElement, Table


def get_data_elementLUT(rows):
    """
    Create all new data elements based on the spread sheet.

    Data elements are versioned, but they will be implicitly versioned
    by being attatched to versioned columns
    """

    csv_de_names = set(row["Data_Element"] for row in rows)
    data_elements = DataElement.objects.bulk_create(
        DataElement(name=name, slug=slugify(name)) for name in csv_de_names
    )
    return {de.name: de for de in data_elements}


def get_tables(tableLUT, addresses):
    for address in addresses:
        database_name, _, schema_table = address.partition(".")

        if not schema_table:
            # Example: NHSE_SUSPlus_Live.dbo.tbl_Data_SEM_OPA
            raise Exception(
                f"Present_In field not in the expected format 'Database.Schema.Table': {address}"
            )

        schema_name, _, table_name = schema_table.partition(".")

        yield tableLUT[database_name][schema_name][table_name]


def import_from_db(version):
    query = "SELECT * from vw_Export_Standard_Definitions"
    rows = api.query(query)

    tables = Table.objects.select_related("schema", "schema__database").filter(
        schema__database__version=version
    )
    tableLUT = collections.defaultdict(lambda: collections.defaultdict(dict))
    for table in tables:
        tableLUT[table.schema.database.name][table.schema.name][table.name] = table

    data_elementLUT = get_data_elementLUT(rows)

    columns = []
    for row in rows:
        # A Column is an instance of a DataElement and can be present in many
        # Tables.  Each "address" describes Database -> Schema -> Table.
        addresses = row["Present_In"].split(", ")
        tables = list(get_tables(tableLUT, addresses))

        # Build a Column for each Table found.
        for table in tables:
            link = row["Link"] if row["Link"] != "N/A" else ""

            columns.append(
                Column(
                    data_element=data_elementLUT[row["Data_Element"]],
                    table=table,
                    name=row["Item_Name"],
                    description=row["Description"],
                    derivation=row["NCDR_Derivation_Methodology"],
                    data_type=row["Data_Type"],
                    is_derived_item=row["Is_Derived_Item"].lower().startswith("yes"),
                    link=link,
                )
            )
            # batch create the columns in 100s
            if len(columns) > 100:
                Column.objects.bulk_create(columns)
                columns = []

    # create everything that's left
    Column.objects.bulk_create(columns)
