import pyodbc
from django.conf import settings


def query(someQuery):
    connection_str = ";".join(
        [
            "DRIVER={ODBC Driver 17 for SQL Server}",
            f"SERVER=tcp:{settings.UPSTREAM_DB_HOST}",
            f"DATABASE={settings.UPSTREAM_DB_DATABASE}",
            f"UID={settings.UPSTREAM_DB_USERNAME}",
            f"PWD={settings.UPSTREAM_DB_PASSWORD}",
        ]
    )
    results = []
    with pyodbc.connect(connection_str) as conn:
        with conn.cursor() as cur:
            rows = cur.execute(someQuery).fetchall()
            columns = [column[0] for column in cur.description]
            for row in rows:
                results.append(dict(zip(columns, row)))
    return results
