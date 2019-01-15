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

        for row in rows:
            Theme.objects.create(number=row["Number"], name=row["Theme"])
