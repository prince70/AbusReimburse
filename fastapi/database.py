import logging
import os
import pyodbc
from datetime import date, datetime

DB_SERVER = "192.168.41.57"
DB_DATABASE = "Reimbursement"
DB_USERNAME = "sa"
DB_PASSWORD = "3518i"
DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
logger = logging.getLogger(__name__)


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


def ensure_expense_reports_updated_at_column():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        IF COL_LENGTH('expense_reports', 'updated_at') IS NULL
        BEGIN
            ALTER TABLE expense_reports ADD updated_at DATETIME NULL;

            UPDATE expense_reports
            SET updated_at = COALESCE(finance_time, approver_time, created_at, GETDATE())
            WHERE updated_at IS NULL;

            IF NOT EXISTS (
                SELECT 1
                FROM sys.default_constraints dc
                JOIN sys.columns c ON c.default_object_id = dc.object_id
                JOIN sys.tables t ON t.object_id = c.object_id
                WHERE t.name = 'expense_reports' AND c.name = 'updated_at'
            )
            BEGIN
                ALTER TABLE expense_reports
                ADD CONSTRAINT DF_expense_reports_updated_at DEFAULT GETDATE() FOR updated_at;
            END
        END
        """)
        conn.commit()
    except Exception:
        logger.exception("Failed to ensure expense_reports.updated_at exists")
        raise
    finally:
        conn.close()


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
