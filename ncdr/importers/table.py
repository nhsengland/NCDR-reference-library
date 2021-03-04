from ncdr.importers import db_api as api
from ncdr.models import Database, Schema, Table


def create_databases(version):
    query = "select * from tbl_Export_Standard_DB_Structure where [Schema] = ''"
    results = api.query(query)
    for row in results:
        Database.objects.create(
            name=row["Database"],
            display_name=row["Name"],
            description=row["Description"],
            link=row["Link"],
            version=version,
        )


def create_schemas(version):
    query = "select * from tbl_Export_Standard_DB_Structure where [Schema] \
<> '' and [Table or View] = 'N/A'"
    results = api.query(query)
    for row in results:
        database = Database.objects.get(version=version, name=row["Database"])
        Schema.objects.create(name=row["Schema"], database=database)


def create_tables_or_views(version):
    query = "select * from tbl_Export_Standard_DB_Structure where [Schema] \
<> '' and [Table or View] <> 'N/A'"
    results = api.query(query)
    for row in results:
        schema = Schema.objects.get(
            name=row["Schema"],
            database__name=row["Database"],
            database__version=version,
        )
        Table.objects.create(
            name=row["Table/View"],
            description=row["Description"],
            link=row["Link"],
            is_table=row["Table or View"] == "Table",
            date_range=row["Date_Range"],
            schema=schema,
        )


def import_from_db(version):
    create_databases(version)
    create_schemas(version)
    create_tables_or_views(version)
