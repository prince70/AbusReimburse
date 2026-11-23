from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_connection, rows_to_dicts

router = APIRouter()


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


@router.get("/audit")
def get_audit_list(current_approver: int = Query(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM expense_reports WHERE status='待审' AND approver_id=? ORDER BY created_at DESC",
        current_approver
    )
    rows = rows_to_dicts(cursor.fetchall(), cursor)
    conn.close()
    return {"code": 0, "data": serialize(rows)}


@router.post("/audit/{report_id}/approve")
def manager_approve(report_id: int, approver_role: str = Query(...), approver_id: int = Query(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM expense_reports WHERE id=?", report_id)
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="报销单不存在")
    if row[0] != "待审":
        raise HTTPException(status_code=400, detail="该报销单不处于待审状态")
    now = datetime.now()
    # 自动分配财务人员（取第一个财务管理员）
    cursor.execute("SELECT id, name FROM [user] WHERE role='财务管理员' ORDER BY id")
    finance_row = cursor.fetchone()
    finance_id = finance_row[0] if finance_row else None
    finance_name = finance_row[1] if finance_row else None
    cursor.execute(
        "UPDATE expense_reports SET status='已批', approver_time=?, finance_status='待审', "
        "finance_id=?, finance_name=?, updated_at=? WHERE id=?",
        now, finance_id, finance_name, now, report_id
    )
    conn.commit()
    conn.close()
    return {"code": 0, "message": "审批通过"}


@router.post("/audit/{report_id}/reject")
def manager_reject(report_id: int, body: RejectBody, approver_role: str = Query(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM expense_reports WHERE id=?", report_id)
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="报销单不存在")
    now = datetime.now()
    cursor.execute(
        "UPDATE expense_reports SET status='退回', reject_reason=?, approver_time=?, updated_at=? WHERE id=?",
        body.reject_reason, now, now, report_id
    )
    conn.commit()
    conn.close()
    return {"code": 0, "message": "已退回"}
