import pyodbc

conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=192.168.41.57;'
    'DATABASE=Reimbursement;'
    'UID=sa;PWD=3518i;'
    'TrustServerCertificate=yes;'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# 创建 user 表
try:
    cursor.execute('''
    CREATE TABLE [user] (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(50) NOT NULL,
        username NVARCHAR(50) NOT NULL UNIQUE,
        password NVARCHAR(100) NOT NULL,
        role NVARCHAR(20) NOT NULL DEFAULT N'员工',
        department NVARCHAR(50) NULL,
        workshop NVARCHAR(50) NULL,
        supervisor_id INT NULL,
        created_at DATETIME NOT NULL DEFAULT GETDATE()
    )''')
    print('user 表创建成功')
except Exception as e:
    print(f'user 表: {e}')

# 创建 expense_reports 表
try:
    cursor.execute('''
    CREATE TABLE expense_reports (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NOT NULL,
        applicant NVARCHAR(50) NOT NULL,
        input_date DATE NOT NULL,
        approver_id INT NULL,
        approver_name NVARCHAR(50) NULL,
        approver_time DATETIME NULL,
        total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
        status NVARCHAR(10) NOT NULL DEFAULT N'待审',
        reject_reason NVARCHAR(500) NULL,
        finance_id INT NULL,
        finance_name NVARCHAR(50) NULL,
        finance_status NVARCHAR(10) NULL,
        finance_reason NVARCHAR(500) NULL,
        finance_time DATETIME NULL,
        created_at DATETIME NOT NULL DEFAULT GETDATE(),
        updated_at DATETIME NOT NULL DEFAULT GETDATE()
    )''')
    print('expense_reports 表创建成功')
except Exception as e:
    print(f'expense_reports 表: {e}')

# 创建 expense_items 表
try:
    cursor.execute('''
    CREATE TABLE expense_items (
        id INT IDENTITY(1,1) PRIMARY KEY,
        report_id INT NOT NULL,
        date DATE NOT NULL,
        category NVARCHAR(50) NOT NULL,
        sub_cat NVARCHAR(50) NULL,
        reason NVARCHAR(200) NOT NULL,
        department NVARCHAR(50) NOT NULL,
        workshop NVARCHAR(50) NULL,
        licence NVARCHAR(20) NULL,
        invoice NVARCHAR(50) NULL,
        attachments INT NOT NULL DEFAULT 0,
        amount DECIMAL(12,2) NOT NULL DEFAULT 0,
        CONSTRAINT FK_items_report FOREIGN KEY (report_id) REFERENCES expense_reports(id)
    )''')
    print('expense_items 表创建成功')
except Exception as e:
    print(f'expense_items 表: {e}')

conn.commit()

# 插入初始用户 (密码: admin123 的MD5)
try:
    cursor.execute("INSERT INTO [user] (name, username, password, role) VALUES (N'系统管理员', 'admin', '0192023a7bbd73250516f069df18b500', N'系统管理员')")
    print('插入 admin 用户成功')
except:
    print('admin 用户已存在')

# 插入财务用户 (密码: finance123 的MD5)
try:
    cursor.execute("INSERT INTO [user] (name, username, password, role, department) VALUES (N'财务管理员', 'finance', '3f5c7f9a0e8c4b5e5a1e2d8f6a3b9c7d', N'财务管理员', N'财务部')")
    print('插入 finance 用户成功')
except:
    print('finance 用户已存在')

conn.commit()

# 查询所有用户
cursor.execute('SELECT id, name, username, role FROM [user]')
rows = cursor.fetchall()
print('\n当前用户:')
for r in rows:
    print(f'  ID:{r[0]} Name:{r[1]} Username:{r[2]} Role:{r[3]}')

conn.close()
print('\n数据库初始化完成!')