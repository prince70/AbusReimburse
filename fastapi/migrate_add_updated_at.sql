USE [Reimbursement]
GO

IF COL_LENGTH('expense_reports', 'updated_at') IS NULL
BEGIN
  ALTER TABLE expense_reports ADD updated_at DATETIME NULL

  UPDATE expense_reports
  SET updated_at = COALESCE(finance_time, approver_time, created_at, GETDATE())
  WHERE updated_at IS NULL

  IF NOT EXISTS (
    SELECT 1
    FROM sys.default_constraints dc
    JOIN sys.columns c ON c.default_object_id = dc.object_id
    JOIN sys.tables t ON t.object_id = c.object_id
    WHERE t.name = 'expense_reports' AND c.name = 'updated_at'
  )
  BEGIN
    ALTER TABLE expense_reports
    ADD CONSTRAINT DF_expense_reports_updated_at DEFAULT GETDATE() FOR updated_at
  END
END
GO
