"""
Load a csv into the ncdr
"""
import os
from django.core.management.base import BaseCommand
from csv_schema.csv_import import row_loader, table_loader

ROW_FILE_DIR = "data/csvs/rows"
TABLE_FILE_DIR = "data/csvs/database_and_tables"


class Command(BaseCommand):
    """
    Loads in all csv files in the FILE_DIR
    """
    def handle(self, *args, **options):
        all_table_files = [i for i in os.listdir(TABLE_FILE_DIR) if i.endswith(".csv")]
        for f in all_table_files:
            table_loader.load_file(os.path.join(TABLE_FILE_DIR, f))

        all_row_files = [i for i in os.listdir(ROW_FILE_DIR) if i.endswith(".csv")]
        for f in all_row_files:
            row_loader.load_file(os.path.join(ROW_FILE_DIR, f))
