"""
Load a csv of table columns into the ncdr
"""
from django.core.management.base import BaseCommand

from csv_schema.csv_import import column_loader


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", type=str)

    def handle(self, file_name, *args, **options):
        column_loader.load_file(file_name)
