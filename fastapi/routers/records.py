from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from database import get_connection, dict_from_row, rows_to_dicts

router = APIRouter()


class ExpenseItem(BaseModel):
    date: str
    category: str
    sub_cat: Optional[str] = None
    reason: str
    department: str
    workshop: Optional[str] = None
    licence: Optional[str] = None
    invoice: Optional[str] = None
    attachments: int = 0
    amount: float


class CreateReportBody(BaseModel):
    user_id: int
    applicant: str
    input_date: str
    approver_id: int
    approver_name: str
    total_amount: float
    items: List[ExpenseItem]


class UpdateReportBody(BaseModel):
    input_date: Optional[str] = None
    approver_id: Optional[int] = None
    approver_name: Optional[str] = None
    total_amount: Optional[float] = None
    items: Optional[List[ExpenseItem]] = None


def serialize_row(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(v, (date, datetime)):
            d[k] = str(v)
    return d


@router.get("/record")
def get_records(
    user_id: int = Query(...),
    role: str = Query(...),
    page: int = Query(1),
    page_size: int = Query(20)
):
    conn = get_connection()
    cursor = conn.cursor()
    offset = (page - 1) * page_size
    if role == "员工":
        cursor.execute(
            "SELECT * FROM expense_reports WHERE user_id=? ORDER BY created_at DESC "
            "OFFSET ? ROWS FETCH NEXT ? ROWS ONLY",
            user_id, offset, page_size
        )
    else:
        cursor.execute(
            "SELECT * FROM expense_reports ORDER BY created_at DESC "
            "OFFSET ? ROWS FETCH NEXT ? ROWS ONLY",
            offset, page_size
        )
    rows = cursor.fetchall()
    result = [serialize_row(r) for r in rows_to_dicts(rows, cursor)]
    if role == "员工":
        cursor.execute("SELECT COUNT(*) FROM expense_reports WHERE user_id=?", user_id)
    else:
        cursor.execute("SELECT COUNT(*) FROM expense_reports")
    total = cursor.fetchone()[0]
    conn.close()
    return {"code": 0, "data": result, "total": total}


@router.post("/record")
def create_record(body: CreateReportBody):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute(
        "INSERT INTO expense_reports (user_id, applicant, input_date, approver_id, approver_name, "
        "total_amount, status, created_at) "
        "OUTPUT INSERTED.id "
        "VALUES (?, ?, ?, ?, ?, ?, '待审', ?)",
        body.user_id, body.applicant, body.input_date, body.approver_id,
        body.approver_name, body.total_amount, now
    )
    report_id = cursor.fetchone()[0]
    for item in body.items:
        cursor.execute(
            "INSERT INTO expense_items (report_id, date, category, sub_cat, reason, department, "
            "workshop, licence, invoice, attachments, amount) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            report_id, item.date, item.category, item.sub_cat, item.reason,
            item.department, item.workshop, item.licence, item.invoice,
            item.attachments, item.amount
        )
    conn.commit()
    conn.close()
    return {"code": 0, "id": report_id, "message": "报销单创建成功"}


@router.get("/record/finance/approved")
def get_finance_approved(
    user_id: int = Query(...),
    role: str = Query(...)
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM expense_reports WHERE status='已批' ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    result = [serialize_row(r) for r in rows_to_dicts(rows, cursor)]
    conn.close()
    return {"code": 0, "data": result}


@router.get("/record/{report_id}")
def get_record(report_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expense_reports WHERE id=?", report_id)
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="报销单不存在")
    report = serialize_row(dict_from_row(row, cursor))
    cursor.execute("SELECT * FROM expense_items WHERE report_id=? ORDER BY date", report_id)
    items = [serialize_row(r) for r in rows_to_dicts(cursor.fetchall(), cursor)]
    report["items"] = items
    conn.close()
    return {"code": 0, "data": report}


@router.put("/record/{report_id}")
def update_record(report_id: int, body: UpdateReportBody):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM expense_reports WHERE id=?", report_id)
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="报销单不存在")
    if row[0] != "待审":
        raise HTTPException(status_code=400, detail="只能编辑待审状态的报销单")
    cursor.execute(
        "UPDATE expense_reports SET input_date=?, approver_id=?, approver_name=?, "
        "total_amount=? WHERE id=?",
        body.input_date, body.approver_id, body.approver_name,
        body.total_amount, report_id
    )
    if body.items is not None:
        cursor.execute("DELETE FROM expense_items WHERE report_id=?", report_id)
        for item in body.items:
            cursor.execute(
                "INSERT INTO expense_items (report_id, date, category, sub_cat, reason, department, "
                "workshop, licence, invoice, attachments, amount) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                report_id, item.date, item.category, item.sub_cat, item.reason,
                item.department, item.workshop, item.licence, item.invoice,
                item.attachments, item.amount
            )
    conn.commit()
    conn.close()
    return {"code": 0, "message": "更新成功"}


@router.delete("/record/{report_id}")
def delete_record(report_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM expense_reports WHERE id=?", report_id)
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="报销单不存在")
    if row[0] != "待审":
        raise HTTPException(status_code=400, detail="只能删除待审状态的报销单")
    cursor.execute("DELETE FROM expense_items WHERE report_id=?", report_id)
    cursor.execute("DELETE FROM expense_reports WHERE id=?", report_id)
    conn.commit()
    conn.close()
    return {"code": 0, "message": "删除成功"}
