import collections
import csv

from django.db import transaction

from ...models import Column, DataElement, Table


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


@transaction.atomic
def load_file(file_name):
    with open(file_name, "r", encoding="Windows-1252") as f:
        f.readline()  # ignore the first line since it's blank
        rows = list(csv.DictReader(f, delimiter="¬"))

    tables = Table.objects.select_related("schema", "schema__database")
    tableLUT = collections.defaultdict(lambda: collections.defaultdict(dict))
    for table in tables:
        tableLUT[table.schema.database.name][table.schema.name][table.name] = table

    columns = []
    for row in rows:
        data_element, _ = DataElement.objects.get_or_create(name=row["Data_Element"])

        # A Column is an instance of a DataElement and can be present in many
        # Tables.  Each "address" describes Database -> Schema -> Table.
        addresses = row["Present_In"].split(", ")
        tables = list(get_tables(tableLUT, addresses))

        # Build a Column for each Table found.
        for table in tables:
            link = row["Link"] if row["Link"] != "N/A" else ""

            columns.append(
                Column(
                    data_element=data_element,
                    table=table,
                    name=row["Item_Name"],
                    description=row["Description"],
                    derivation=row["NCDR_Derivation_Methodology"],
                    data_type=row["Data_Type"],
                    is_derived_item=row["Is_Derived_Item"].lower().startswith("yes"),
                    link=link,
                )
            )

    Column.objects.bulk_create(columns)
