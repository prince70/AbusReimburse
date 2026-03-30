from fastapi import APIRouter, Query
from database import get_connection, rows_to_dicts

router = APIRouter()


@router.get("/departments")
def get_departments():
    """获取部门列表"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, department
        FROM Reimbursement.dbo.department
        WHERE id BETWEEN 1 AND 15
        ORDER BY id
    """)
    rows = cursor.fetchall()
    result = [r[1] for r in rows] if rows else []
    conn.close()
    return {"code": 0, "data": result}


@router.get("/categories")
def get_categories():
    """获取类别及其子类"""
    conn = get_connection()
    cursor = conn.cursor()
    # 从 category 和 sub_category 表查询
    cursor.execute("""
        SELECT c.id, c.category, s.sub_category
        FROM Reimbursement.dbo.category c
        LEFT JOIN Reimbursement.dbo.sub_category s ON c.id = s.category_id
        WHERE c.id BETWEEN 1 AND 22
        ORDER BY c.id, s.id
    """)
    rows = cursor.fetchall()
    cat_dict = {}
    for r in rows:
        cat_id = r[0]
        cat_name = r[1] if r[1] else ''
        sub_name = r[2] if r[2] else ''
        if cat_name and cat_name not in cat_dict:
            cat_dict[cat_name] = []
        if cat_name and sub_name and sub_name not in cat_dict[cat_name]:
            cat_dict[cat_name].append(sub_name)
    result = [{"name": k, "sub": v} for k, v in cat_dict.items()]
    conn.close()
    return {"code": 0, "data": result}


@router.get("/sub_categories")
def get_sub_categories():
    """获取所有子类 - 从 expense_items 表查询 sub_cat"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT sub_cat
        FROM expense_items
        WHERE sub_cat IS NOT NULL AND LTRIM(RTRIM(sub_cat)) <> ''
        ORDER BY sub_cat
    """)
    rows = cursor.fetchall()
    result = [r[0] for r in rows]
    conn.close()
    return {"code": 0, "data": result}


@router.get("/workshops")
def get_workshops():
    """获取车间列表 - 从用户表Workshop字段查询"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT workshop 
        FROM [user] 
        WHERE workshop IS NOT NULL 
          AND LTRIM(RTRIM(workshop)) <> ''
        ORDER BY workshop
    """)
    rows = cursor.fetchall()
    result = [r[0] for r in rows]
    conn.close()
    return {"code": 0, "data": result}


@router.get("/license_plates")
def get_license_plates():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT licence FROM expense_items WHERE licence IS NOT NULL AND licence != '' ORDER BY licence")
    rows = cursor.fetchall()
    result = [r[0] for r in rows]
    conn.close()
    return {"code": 0, "data": result}


@router.get("/reports/statistics")
def get_statistics(user_id: int = Query(...), role: str = Query(...)):
    conn = get_connection()
    cursor = conn.cursor()
    if role == "员工":
        cursor.execute(
            "SELECT COUNT(*) as total, "
            "SUM(CASE WHEN status='待审' THEN 1 ELSE 0 END) as pending, "
            "SUM(CASE WHEN status='已批' THEN 1 ELSE 0 END) as approved, "
            "SUM(CASE WHEN status='退回' THEN 1 ELSE 0 END) as rejected, "
            "ISNULL(SUM(total_amount),0) as total_amount "
            "FROM expense_reports WHERE user_id=?",
            user_id
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) as total, "
            "SUM(CASE WHEN status='待审' THEN 1 ELSE 0 END) as pending, "
            "SUM(CASE WHEN status='已批' THEN 1 ELSE 0 END) as approved, "
            "SUM(CASE WHEN status='退回' THEN 1 ELSE 0 END) as rejected, "
            "ISNULL(SUM(total_amount),0) as total_amount "
            "FROM expense_reports"
        )
    row = cursor.fetchone()
    cols = [d[0] for d in cursor.description]
    data = dict(zip(cols, row))
    conn.close()
    return {"code": 0, "data": data}


@router.get("/reports/department")
def get_department_report():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ei.department, ISNULL(SUM(ei.amount),0) as total "
        "FROM expense_items ei "
        "JOIN expense_reports er ON ei.report_id = er.id "
        "WHERE er.status='已批' "
        "GROUP BY ei.department ORDER BY total DESC"
    )
    rows = cursor.fetchall()
    result = [{"department": r[0], "total": float(r[1])} for r in rows]
    conn.close()
    return {"code": 0, "data": result}


@router.get("/reports/monthly")
def get_monthly_report():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT FORMAT(input_date,'yyyy-MM') as month, ISNULL(SUM(total_amount),0) as total "
        "FROM expense_reports WHERE status='已批' "
        "GROUP BY FORMAT(input_date,'yyyy-MM') ORDER BY month DESC"
    )
    rows = cursor.fetchall()
    result = [{"month": r[0], "total": float(r[1])} for r in rows]
    conn.close()
    return {"code": 0, "data": result}
