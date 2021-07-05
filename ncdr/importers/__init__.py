from django.db import transaction
from django.utils import timezone
import structlog
import traceback
import time
from ncdr.importers import column, grouping, table, db_api
from ncdr.models import Version

logger = structlog.get_logger("ncdr")


def get_upstream_time_stamp():
    """
    Get the upstream timestamp which tells us if we should refresh
    """
    query = "Select * from tbl_Export_Standard_RefreshDateTime"
    # Note access to the upstream db is IP address dependent.
    return timezone.make_aware(db_api.query(query)[0]["Refresh_DateTime"])


@transaction.atomic
def check_and_import():
    start = time.time()
    try:
        upstream_ts = get_upstream_time_stamp()
        latest = Version.objects.order_by("-upstream_updated_ts").first()
        if upstream_ts > latest:
            version = Version.objects.create(
                is_published=False, upstream_updated_ts=upstream_ts
            )
            table.import_from_db(version)
            column.import_from_db(version)
            grouping.import_from_db(version)
            end = time.time()
            logger.info(f"Version loaded in {(end-start)/60} minutes")
    except Exception:
        logger.error(f"Unable to load in NCDR \n{traceback.format_exc()}")
