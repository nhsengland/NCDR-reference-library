"""
Load a csv into the ncdr
"""
import os
from django.core.management.base import BaseCommand
from csv_schema.csv_import import column_loader, table_loader

COLUMN_FILE_DIR = "data/csvs/columns"
TABLE_FILE_DIR = "data/csvs/database_and_tables"


class Command(BaseCommand):
    """
    Loads in all csv files in the FILE_DIR
    """
    def handle(self, *args, **options):
        all_table_files = [
            i for i in os.listdir(TABLE_FILE_DIR) if i.endswith(".csv")
        ]
        for f in all_table_files:
            table_loader.load_file(os.path.join(TABLE_FILE_DIR, f))

        all_column_files = [
            i for i in os.listdir(COLUMN_FILE_DIR) if i.endswith(".csv")
        ]
        for f in all_column_files:
            column_loader.load_file(os.path.join(COLUMN_FILE_DIR, f))
