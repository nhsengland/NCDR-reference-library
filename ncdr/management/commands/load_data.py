import os

from django.core.management.base import BaseCommand, CommandError

from ...models import Column, Database, DataElement, Grouping, Table

CSVS_DIR = "data/csvs"
versions = os.listdir(CSVS_DIR)


class Command(BaseCommand):
    """Load in CSV files"""

    def add_arguments(self, parser):
        parser.add_argument("--data-version", default=max(versions))

    def clear_data(self):
        DataElement.objects.all().delete()
        Column.objects.all().delete()
        Grouping.objects.all().delete()
        Table.objects.all().delete()
        Database.objects.all().delete()

    def handle(self, *args, **options):
        version = options["data_version"]

        if version not in versions:
            raise CommandError(
                f"Unknown version '{version}', please pick from: {', '.join(versions)}"
            )

        path = os.path.join(CSVS_DIR, version)
        self.stdout.write(f"Importing data from {path}")

        self.clear_data()

        if version == "1":
            from ncdr.importers.v1 import column, grouping, table

            table.load_file(os.path.join(path, "vw_Export_Standard_DB_Structure.csv"))

            column.load_file(os.path.join(path, "vw_Export_Standard_Definitions.csv"))

            grouping.load_file(
                os.path.join(path, "vw_Export_Standard_GroupingMapping.csv")
            )
