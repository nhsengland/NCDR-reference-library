"""
Load a csv into the ncdr
"""
from django.core.management.base import BaseCommand
from csv_schema import csv_loader


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)

    def handle(self, file_name, *args, **options):
        csv_loader.load_file(file_name)
