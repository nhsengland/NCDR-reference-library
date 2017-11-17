"""
Load a csv of database and table descriptions into the ncdr
"""
import os
from django.core.management.base import BaseCommand
from csv_schema.csv_import import table_loader


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)

    def handle(self, file_name, *args, **options):
        row_loader.table_loader(file_name)
