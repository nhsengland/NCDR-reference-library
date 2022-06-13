import pyodbc
from django.conf import settings


def get_connection_string():
    if settings.UDAL:
        return ";".join(
            [
                "DRIVER={ODBC Driver 17 for SQL Server}",
                f"SERVER=tcp:{settings.NCDR_UPSTREAM_DB_HOST}",
                f"DATABASE={settings.NCDR_UPSTREAM_DB_DATABASE}",
                f"UID={settings.NCDR_UPSTREAM_DB_USERNAME}",
                f"PWD={settings.NCDR_UPSTREAM_DB_PASSWORD}",
            ]
        )
    else:
        return ";".join(
            [
                "DRIVER={ODBC Driver 17 for SQL Server}",
                f"SERVER=tcp:{settings.UDAL_UPSTREAM_DB_HOST}",
                f"DATABASE={settings.UDAL_UPSTREAM_DB_DATABASE}",
                f"UID={settings.UDAL_UPSTREAM_DB_USERNAME}",
                f"PWD={settings.UDAL_UPSTREAM_DB_PASSWORD}",
            ]
        )


def query(someQuery):
    connection_str = get_connection_string()
    results = []
    with pyodbc.connect(connection_str) as conn:
        with conn.cursor() as cur:
            rows = cur.execute(someQuery).fetchall()
            columns = [column[0] for column in cur.description]
            for row in rows:
                results.append(dict(zip(columns, row)))
    return results
