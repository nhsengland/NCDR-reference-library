from django.db import transaction
import structlog
import traceback
from ncdr.importers import column, grouping, table, db_api
from ncdr.models import Version

logger = structlog.get_logger("ncdr")


def check():
    """
    They will provide a time stamp for a version to let us know if
    when a new version is available. This is not yet done.
    """
    query = "Select * from tbl_Export_Standard_RefreshDateTime"
    result = db_api.query(query)[0]["Refresh_DateTime"]
    if result > Version.objects.order_by("-created_at")[0].created_at:
        return True


@transaction.atomic
def check_and_import():
    try:
        if check():
            version = Version.objects.create(is_published=False)
            table.import_from_db(version)
            column.import_from_db(version)
            grouping.import_from_db(version)
    except Exception:
        logger.error(f"Unable to load in NCDR \n{traceback.format_exc()}")
