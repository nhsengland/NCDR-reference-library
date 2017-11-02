"""
Load a csv into the ncdr
"""
import os
from django.core.management.base import BaseCommand
from csv_schema import csv_loader

FILE_DIR = "data/csvs"


class Command(BaseCommand):
    """
    Loads in all csv files in the FILE_DIR
    """
    def handle(self, *args, **options):
        all_files = [i for i in os.listdir(FILE_DIR) if i.endswith(".csv")]
        for f in all_files:
            csv_loader.load_file(os.path.join(FILE_DIR, f))
