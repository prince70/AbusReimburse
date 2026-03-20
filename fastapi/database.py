import os
import pyodbc
from datetime import date, datetime

DB_SERVER = "192.168.41.57"
DB_DATABASE = "Reimbursement"
DB_USERNAME = "sa"
DB_PASSWORD = "3518i"
DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")


def get_connection():
    conn_str = (
        f'DRIVER={{{DRIVER}}};'
        f'SERVER={DB_SERVER};'
        f'DATABASE={DB_DATABASE};'
        f'UID={DB_USERNAME};'
        f'PWD={DB_PASSWORD};'
        f'TrustServerCertificate=yes;'
    )
    return pyodbc.connect(conn_str)


def dict_from_row(row, cursor) -> dict:
    if row is None:
        return {}
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def rows_to_dicts(rows, cursor) -> list:
    if not rows:
        return []
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in rows]