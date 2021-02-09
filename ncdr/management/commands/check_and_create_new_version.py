from django.core.management.base import BaseCommand

from ncdr.importers import check_and_import
from ncdr.models import Version


class Command(BaseCommand):
    def handle(self, *args, **options):
        Version.create(is_published=False)
        check_and_import()
