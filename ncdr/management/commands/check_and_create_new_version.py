from django.core.management.base import BaseCommand

from ncdr.importers import check_and_import


class Command(BaseCommand):
    def handle(self, *args, **options):
        check_and_import()
