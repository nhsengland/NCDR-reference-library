import io

import structlog
from django.db import transaction
from django.utils import timezone

from . import column, grouping, table
from ..models import Version

logger = structlog.get_logger("ncdr")


def to_text(f):
    """
    Convert the given file from binary to a 'Windows - 1252' text file.

    The files uploaded come from a system which generates them with 'Windows -
    1252' encoding.  We've stored those behind Django's models.FileField which
    returns a models.FieldFile when accessed.  This class also opens the file
    for us to try and be helpful, however it opens the files in binary mode
    which is less than helpful.  This method re-encodes the file by reading it
    into StringIO which quacks like a File.

    https://andromedayelton.com/2017/04/25/adventures-with-parsing-django-uploaded-csv-files-in-python3/
    """
    return io.StringIO(f.read().decode("Windows - 1252"))


@transaction.atomic
def import_data(version_pk):

    version = Version.objects.get(pk=version_pk)

    # bind version ID to the logger
    log = logger.bind(version=version.pk)

    try:
        table.load_file(to_text(version.db_structure), version)
        column.load_file(to_text(version.definitions), version)
        grouping.load_file(to_text(version.grouping_mapping), version)
    except Exception:
        # log the exception, whatever it is so we can track down errors later.
        log.exception("CSV processing failed")

        # reraise the exception to trigger a ROLLBACK via transaction.atomic()
        raise

    version.last_process_at = timezone.now()
    version.save()
