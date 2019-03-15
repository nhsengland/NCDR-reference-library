import csv

from django.core.management.base import BaseCommand

from ...models import Theme


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        path = options["path"]

        with open(options["path"], "r") as f:
            delimiter = "\t" if path.endswith(".tsv") else ","
            rows = list(csv.DictReader(f, delimiter=delimiter, quotechar='"'))

        Theme.objects.bulk_create(
            Theme(number=row["Number"], name=row["Theme"]) for row in rows
        )

        self.stdout.write(self.style.SUCCESS("Added Themes"))
