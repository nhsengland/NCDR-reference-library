import collections
import csv

from ..models import Column, DataElement, Table


def get_data_elementLUT(rows):
    """
    Build a lookup table of DataElement instances keyed by their name

    This replaces a get_or_create in the outer loop body below.  Each iteration
    would get call the get_or_create for the Column instantiation to use.
    During the move to import CSVs via webform it was noted importing took ~90s
    on a local machine.  However when that same import function, import_data at
    the time of writing, was called by an RQ worker it ran in ~10s.  After much
    digging it was discovered that the aggregate time cost for the
    get_or_creates calls was the cause, again only when called directly from
    the view.  Rather than waste more time building an extension on the rabbit
    hole the sensible decision to use a precomputed lookup table was taken.

    This function builds that table, creating any missing DataElements in the
    process.
    """
    existing_de_names = set(DataElement.objects.values_list("name", flat=True))
    csv_de_names = set(row["Data_Element"] for row in rows)
    missing_de_names = csv_de_names - existing_de_names
    DataElement.objects.bulk_create(DataElement(name=name) for name in missing_de_names)

    return {de.name: de for de in DataElement.objects.all()}


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


def load_file(fd, version):
    fd.readline()  # ignore the first line since it's blank
    rows = list(csv.DictReader(fd, delimiter="¬"))

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

    Column.objects.bulk_create(columns)
