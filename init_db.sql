-- ============================================
-- 报销管理系统 数据库初始化脚本
-- 数据库: Reimbursement
-- SQL Server 192.168.10.202
-- ============================================

USE [Reimbursement]
GO

-- 用户表
IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'user' AND type = 'U')
BEGIN
  CREATE TABLE [user] (
    id            INT IDENTITY(1,1) PRIMARY KEY,
    name          NVARCHAR(50)  NOT NULL,
    username      NVARCHAR(50)  NOT NULL UNIQUE,
    password      NVARCHAR(100) NOT NULL,
    role          NVARCHAR(20)  NOT NULL DEFAULT N'员工',
    department    NVARCHAR(50)  NULL,
    workshop      NVARCHAR(50)  NULL,
    supervisor_id INT           NULL,
    created_at    DATETIME      NOT NULL DEFAULT GETDATE()
  )
END
GO

-- 报销单主表
IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'expense_reports' AND type = 'U')
BEGIN
  CREATE TABLE expense_reports (
    id             INT IDENTITY(1,1) PRIMARY KEY,
    user_id        INT            NOT NULL,
    applicant      NVARCHAR(50)   NOT NULL,
    input_date     DATE           NOT NULL,
    approver_id    INT            NULL,
    approver_name  NVARCHAR(50)   NULL,
    approver_time  DATETIME       NULL,
    total_amount   DECIMAL(12,2)  NOT NULL DEFAULT 0,
    status         NVARCHAR(10)   NOT NULL DEFAULT N'待审',
    reject_reason  NVARCHAR(500)  NULL,
    finance_id     INT            NULL,
    finance_name   NVARCHAR(50)   NULL,
    finance_status NVARCHAR(10)   NULL,
    finance_reason NVARCHAR(500)  NULL,
    finance_time   DATETIME       NULL,
    created_at     DATETIME       NOT NULL DEFAULT GETDATE(),
    updated_at     DATETIME       NOT NULL DEFAULT GETDATE()
  )
END
GO

-- 报销明细表
IF NOT EXISTS (SELECT * FROM sys.objects WHERE name = 'expense_items' AND type = 'U')
BEGIN
  CREATE TABLE expense_items (
    id          INT IDENTITY(1,1) PRIMARY KEY,
    report_id   INT            NOT NULL,
    date        DATE           NOT NULL,
    category    NVARCHAR(50)   NOT NULL,
    sub_cat     NVARCHAR(50)   NULL,
    reason      NVARCHAR(200)  NOT NULL,
    department  NVARCHAR(50)   NOT NULL,
    workshop    NVARCHAR(50)   NULL,
    licence     NVARCHAR(20)   NULL,
    invoice     NVARCHAR(50)   NULL,
    attachments INT            NOT NULL DEFAULT 0,
    amount      DECIMAL(12,2)  NOT NULL DEFAULT 0,
    CONSTRAINT FK_items_report FOREIGN KEY (report_id) REFERENCES expense_reports(id)
  )
END
GO

-- 初始管理员账户 (密码: admin123 的MD5)
IF NOT EXISTS (SELECT * FROM [user] WHERE username = 'admin')
BEGIN
  INSERT INTO [user] (name, username, password, role)
  VALUES (N'系统管理员', 'admin', '0192023a7bbd73250516f069df18b500', N'系统管理员')
END
GO

-- 初始财务账户 (密码: finance123 的MD5)
IF NOT EXISTS (SELECT * FROM [user] WHERE username = 'finance')
BEGIN
  INSERT INTO [user] (name, username, password, role, department)
  VALUES (N'财务管理员', 'finance', '3f5c7f9a0e8c4b5e5a1e2d8f6a3b9c7d', N'财务管理员', N'财务部')
END
GO

PRINT N'数据库初始化完成'
GO
