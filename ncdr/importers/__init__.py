from django.db import transaction
import structlog
import traceback
from ncdr.importers import column, grouping, table

logger = structlog.get_logger("ncdr")


def check():
    """
    They will provide a time stamp for a version to let us know if
    when a new version is available. This is not yet done.
    """
    return True


@transaction.atomic
def check_and_import(version):
    try:
        if check():
            table.import_from_db(version)
            column.import_from_db(version)
            grouping.import_from_db(version)
    except Exception:
        logger.error(f"Unable to load in NCDR \n{traceback.format_exc()}")
