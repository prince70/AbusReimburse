import http from './http'

export interface ExpenseItem {
  id?: number
  report_id?: number
  date: string
  category: string
  sub_cat?: string
  reason: string
  department: string
  workshop?: string
  licence?: string
  invoice?: string
  attachments: number
  amount: number
}

export interface ExpenseReportModel {
  id?: number
  user_id: number
  applicant: string
  input_date: string
  approver_id: number
  approver_name: string
  approver_time?: string
  total_amount: number
  status?: string
  reject_reason?: string
  finance_id?: number
  finance_name?: string
  finance_status?: string
  finance_reason?: string
  finance_time?: string
  created_at?: string
  updated_at?: string
  items?: ExpenseItem[]
}

export const expenseApi = {
  getRecords: (params: { user_id: number; role: string; page?: number; page_size?: number }) =>
    http.get<any, any>('/api/v1/record', { params }),

  createRecord: (data: ExpenseReportModel) =>
    http.post<any, any>('/api/v1/record', data),

  getRecord: (id: number) =>
    http.get<any, any>(`/api/v1/record/${id}`),

  updateRecord: (id: number, data: Partial<ExpenseReportModel>) =>
    http.put<any, any>(`/api/v1/record/${id}`, data),

  deleteRecord: (id: number) =>
    http.delete<any, any>(`/api/v1/record/${id}`),

  getFinanceApproved: (params: { user_id: number; role: string }) =>
    http.get<any, any>('/api/v1/record/finance/approved', { params }),

  // Audit
  getAuditList: (current_approver: number) =>
    http.get<any, any>('/api/v1/audit', { params: { current_approver } }),

  managerApprove: (id: number, approver_id: number) =>
    http.post<any, any>(`/api/v1/audit/${id}/approve`, {}, {
      params: { approver_role: 'manager', approver_id }
    }),

  managerReject: (id: number, reject_reason: string) =>
    http.post<any, any>(`/api/v1/audit/${id}/reject`, { reject_reason }, {
      params: { approver_role: 'manager' }
    }),

  // Finance audit
  getFinanceAuditList: () =>
    http.get<any, any>('/api/v1/finance/audit'),

  financeApprove: (id: number, finance_id: number) =>
    http.post<any, any>(`/api/v1/finance/audit/${id}/approve`, {}, {
      params: { finance_id }
    }),

  financeReject: (id: number, reject_reason: string) =>
    http.post<any, any>(`/api/v1/finance/audit/${id}/reject`, { reject_reason }),

  // Base data
  getDepartments: () => http.get<any, any>('/api/v1/departments'),
  getCategories: () => http.get<any, any>('/api/v1/categories'),
  getWorkshops: () => http.get<any, any>('/api/v1/workshops'),
  getLicensePlates: () => http.get<any, any>('/api/v1/license_plates'),

  // Reports
  getStatistics: (params: { user_id: number; role: string }) =>
    http.get<any, any>('/api/v1/reports/statistics', { params }),
  getDepartmentReport: () => http.get<any, any>('/api/v1/reports/department'),
  getMonthlyReport: () => http.get<any, any>('/api/v1/reports/monthly')
}
