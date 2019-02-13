import csv

from django.db import transaction

from csv_schema.models import Database, Schema, Table


@transaction.atomic
def load_file(file_name):
    with open(file_name, "r", encoding="Windows-1252") as f:
        f.readline()  # ignore the first line since it's blank
        rows = list(csv.DictReader(f, delimiter="¬"))

    db_rows = filter(
        lambda r: r["SchemaID"] == "0" and r["Table or View"] == "N/A", rows
    )
    for row in db_rows:
        Database.objects.create(
            name=row["Database"],
            display_name=row["Name"],
            description=row["Description"],
            link=row["Link"],
        )

    schema_rows = filter(
        lambda r: r["SchemaID"] != "0" and r["Table or View"] == "N/A", rows
    )
    for row in schema_rows:
        try:
            database = Database.objects.get(name=row["Database"])
        except Database.DoesNotExist:
            print("Unknown database: {}".format(row["Database"]))
            raise

        Schema.objects.create(name=row["Schema"], database=database)

    table_view_rows = filter(lambda r: r["Table or View"] != "N/A", rows)
    for row in table_view_rows:
        try:
            schema = Schema.objects.get(
                name=row["Schema"], database__name=row["Database"]
            )
        except Schema.DoesNotExist:
            print("Unknown database: {}".format(row["Schema"]))
            raise

        Table.objects.create(
            name=row["Table/View"],
            description=row["Description"],
            link=row["Link"],
            is_table=row["Table or View"] == "Table",
            schema=schema,
        )
