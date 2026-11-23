import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from database import get_connection, rows_to_dicts

router = APIRouter()
logger = logging.getLogger(__name__)


class RejectBody(BaseModel):
    reject_reason: str


def serialize(rows: list) -> list:
    result = []
    for r in rows:
        for k, v in r.items():
            if hasattr(v, 'isoformat'):
                r[k] = str(v)
        result.append(r)
    return result


@router.get("/finance/audit")
def get_finance_audit_list():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM expense_reports WHERE status='已批' AND finance_status='待审' ORDER BY created_at DESC"
    )
    rows = rows_to_dicts(cursor.fetchall(), cursor)
    conn.close()
    return {"code": 0, "data": serialize(rows)}


@router.post("/finance/audit/{report_id}/approve")
def finance_approve(report_id: int, finance_id: int = Query(...)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT finance_status FROM expense_reports WHERE id=?", report_id)
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="报销单不存在")
        if row[0] != "待审":
            raise HTTPException(status_code=400, detail="该报销单不处于财务待审状态")
        now = datetime.now()
        cursor.execute(
            "UPDATE expense_reports SET finance_status='已批', finance_id=?, finance_time=?, updated_at=? WHERE id=?",
            finance_id, now, now, report_id
        )
        conn.commit()
        return {"code": 0, "message": "财务审批通过"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Finance approve failed: report_id=%s finance_id=%s", report_id, finance_id)
        raise
    finally:
        conn.close()


@router.post("/finance/audit/{report_id}/reject")
def finance_reject(report_id: int, body: RejectBody):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT finance_status FROM expense_reports WHERE id=?", report_id)
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="报销单不存在")
        now = datetime.now()
        cursor.execute(
            "UPDATE expense_reports SET finance_status='退回', finance_reason=?, finance_time=?, updated_at=? WHERE id=?",
            body.reject_reason, now, now, report_id
        )
        conn.commit()
        return {"code": 0, "message": "已退回"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Finance reject failed: report_id=%s", report_id)
        raise
    finally:
        conn.close()
