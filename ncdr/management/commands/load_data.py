import os

from django.core.management.base import BaseCommand

from ncdr.importers import column, grouping, table

from ...models import Version

CSVS_DIR = "data/csvs"


class Command(BaseCommand):
    """Load in CSV files"""

    def handle(self, *args, **options):
        # FIXME: ???
        path = os.path.join(CSVS_DIR, "1")
        self.stdout.write(f"Importing data from {path}")

        # publish the very first import
        is_published = Version.objects.count() < 2
        import_version = Version.objects.create(is_published=is_published)

        table.load_file(
            os.path.join(path, "vw_Export_Standard_DB_Structure.csv"), import_version
        )

        column.load_file(
            os.path.join(path, "vw_Export_Standard_Definitions.csv"), import_version
        )

        grouping.load_file(
            os.path.join(path, "vw_Export_Standard_GroupingMapping.csv"), import_version
        )
