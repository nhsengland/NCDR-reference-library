import pyodbc
from django.conf import settings


def query(someQuery, **params):
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
    with pyodbc.connect(connection_str, as_dict=True) as conn:
        with conn.cursor() as cur:
            columns = [column[0] for column in cur.description]
            for row in cur.execute(someQuery, params).fetchall():
                results.append(dict(zip(columns, row)))
    return results
