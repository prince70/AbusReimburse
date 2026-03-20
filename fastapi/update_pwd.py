import pyodbc

conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=192.168.41.57;'
    'DATABASE=Reimbursement;'
    'UID=sa;'
    'PWD=3518i;'
    'TrustServerCertificate=yes;'
)

conn = pyodbc.connect(conn_str, autocommit=True)
cursor = conn.cursor()

# 更新密码
import sys
username = sys.argv[1] if len(sys.argv) > 1 else 'admin'
password = sys.argv[2] if len(sys.argv) > 2 else 'admin123'
import hashlib
new_pwd = hashlib.md5(password.encode()).hexdigest()

cursor.execute("UPDATE [user] SET password=? WHERE username=?", (new_pwd, username))
print(f'更新了 {cursor.rowcount} 行: {username} -> {password}')

# 验证
cursor.execute("SELECT password FROM [user] WHERE username=?", (username,))
row = cursor.fetchone()
print(f'{username} 密码: {row[0]}')

conn.close()
print('完成')