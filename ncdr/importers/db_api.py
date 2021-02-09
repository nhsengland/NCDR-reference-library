import pytds
from django.conf import settings


def query(someQuery, **params):
    with pytds.connect(
        settings.UPSTREAM_DB_HOST,
        settings.UPSTREAM_DB_DATABASE,
        settings.UPSTREAM_DB_USERNAME,
        settings.UPSTREAM_DB_PASSWORD,
        as_dict=True,
    ) as conn:
        with conn.cursor() as cur:
            result = cur.execute(someQuery, params).fetchall()
    return result
