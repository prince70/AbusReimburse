from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import hashlib
from database import get_connection, dict_from_row, rows_to_dicts

router = APIRouter()


def md5(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()


class LoginBody(BaseModel):
    username: str
    password: str


class RegisterBody(BaseModel):
    name: str
    username: str
    password: str
    department: Optional[str] = None
    workshop: Optional[str] = None
    supervisor_id: Optional[int] = None


class ProfileBody(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    workshop: Optional[str] = None
    supervisor_id: Optional[int] = None


class ChangePasswordBody(BaseModel):
    user_id: int
    old_password: str
    new_password: str


@router.post("/login")
def login(body: LoginBody):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM [user] WHERE username = ?", body.username)
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    user = dict_from_row(row, cursor)
    stored_pwd = user["password"]
    input_md5 = md5(body.password)
    if stored_pwd == body.password:
        # 明文密码自动升级为MD5
        cursor.execute("UPDATE [user] SET password=? WHERE id=?", input_md5, user["id"])
        conn.commit()
    elif stored_pwd != input_md5:
        conn.close()
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    conn.close()
    user.pop("password", None)
    # 序列化datetime
    for k, v in user.items():
        if hasattr(v, 'isoformat'):
            user[k] = str(v)
    return {"code": 0, "data": user}


@router.post("/register")
def register(body: RegisterBody):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM [user] WHERE username=?", body.username)
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="用户名已存在")
    cursor.execute(
        "INSERT INTO [user] (name, username, password, role, department, workshop, supervisor_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        body.name, body.username, md5(body.password), "员工",
        body.department, body.workshop, body.supervisor_id
    )
    conn.commit()
    conn.close()
    return {"code": 0, "message": "注册成功"}


@router.get("/check-username")
def check_username(username: str = Query(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM [user] WHERE username=?", username)
    exists = cursor.fetchone() is not None
    conn.close()
    return {"exists": exists}


@router.get("/supervisors")
def get_supervisors():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, department FROM [user] WHERE role='经理' ORDER BY name")
    rows = cursor.fetchall()
    result = rows_to_dicts(rows, cursor)
    conn.close()
    return {"code": 0, "data": result}


@router.get("/me/{user_id}")
def get_me(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, username, role, department, workshop, supervisor_id, created_at "
        "FROM [user] WHERE id=?", user_id
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="用户不存在")
    user = dict_from_row(row, cursor)
    for k, v in user.items():
        if hasattr(v, 'isoformat'):
            user[k] = str(v)
    return {"code": 0, "data": user}


@router.put("/profile")
def update_profile(body: ProfileBody, user_id: int = Query(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE [user] SET name=?, department=?, workshop=?, supervisor_id=? WHERE id=?",
        body.name, body.department, body.workshop, body.supervisor_id, user_id
    )
    conn.commit()
    conn.close()
    return {"code": 0, "message": "更新成功"}


@router.post("/change-password")
def change_password(body: ChangePasswordBody):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM [user] WHERE id=?", body.user_id)
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="用户不存在")
    stored = row[0]
    old_md5 = md5(body.old_password)
    if stored != old_md5 and stored != body.old_password:
        raise HTTPException(status_code=400, detail="原密码错误")
    cursor.execute("UPDATE [user] SET password=? WHERE id=?", md5(body.new_password), body.user_id)
    conn.commit()
    conn.close()
    return {"code": 0, "message": "密码修改成功"}


@router.get("/users")
def get_all_users():
    """获取所有用户列表（系统管理员用）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, username, role, department, workshop, created_at FROM [user] ORDER BY id"
    )
    rows = cursor.fetchall()
    result = rows_to_dicts(rows, cursor)
    for user in result:
        for k, v in user.items():
            if hasattr(v, 'isoformat'):
                user[k] = str(v)
    conn.close()
    return {"code": 0, "data": result}


class UpdateUserBody(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    workshop: Optional[str] = None


@router.put("/user")
def update_user(body: UpdateUserBody, user_id: int = Query(...)):
    """更新用户信息（系统管理员用）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 构建更新字段
    fields = []
    values = []
    if body.name is not None:
        fields.append("name=?")
        values.append(body.name)
    if body.role is not None:
        fields.append("role=?")
        values.append(body.role)
    if body.department is not None:
        fields.append("department=?")
        values.append(body.department)
    if body.workshop is not None:
        fields.append("workshop=?")
        values.append(body.workshop)
    if body.password:
        fields.append("password=?")
        values.append(md5(body.password))
    
    if not fields:
        conn.close()
        return {"code": 0, "message": "无需更新"}
    
    values.append(user_id)
    sql = f"UPDATE [user] SET {', '.join(fields)} WHERE id=?"
    cursor.execute(sql, *values)
    conn.commit()
    conn.close()
    return {"code": 0, "message": "更新成功"}


@router.delete("/user")
def delete_user(user_id: int = Query(...)):
    """删除用户（系统管理员用）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM [user] WHERE id=?", user_id)
    conn.commit()
    conn.close()
    return {"code": 0, "message": "删除成功"}
