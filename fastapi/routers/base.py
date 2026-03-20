from fastapi import APIRouter, Query
from database import get_connection, rows_to_dicts

router = APIRouter()


@router.get("/departments")
def get_departments():
    """获取部门列表 - 从用户表Department字段查询"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT Department 
        FROM [user] 
        WHERE Department IS NOT NULL 
          AND LTRIM(RTRIM(Department)) <> ''
        ORDER BY Department
    """)
    rows = cursor.fetchall()
    result = [r[0] for r in rows]
    conn.close()
    return {"code": 0, "data": result}


@router.get("/categories")
def get_categories():
    categories = [
        {"name": "交通费", "sub": ["出租车", "公交", "地铁", "火车", "飞机", "自驾"]},
        {"name": "餐饮费", "sub": ["工作餐", "业务招待"]},
        {"name": "住宿费", "sub": ["酒店", "招待所"]},
        {"name": "办公费", "sub": ["文具", "耗材", "设备"]},
        {"name": "通讯费", "sub": ["话费", "网费"]},
        {"name": "培训费", "sub": ["课程", "教材", "考试"]},
        {"name": "维修费", "sub": ["设备维修", "车辆维修"]},
        {"name": "其他", "sub": []},
    ]
    return {"code": 0, "data": categories}


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
