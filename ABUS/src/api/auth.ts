import http from './http'

export interface UserInfo {
  id: number
  name: string
  username: string
  role: string
  department?: string
  workshop?: string
  supervisor_id?: number
  created_at?: string
}

export const authApi = {
  login: (data: { username: string; password: string }) =>
    http.post< any, any>('/api/auth/login', data),

  register: (data: {
    name: string
    username: string
    password: string
    department?: string
    workshop?: string
    supervisor_id?: number
  }) => http.post<any, any>('/api/auth/register', data),

  checkUsername: (username: string) =>
    http.get<any, any>('/api/auth/check-username', { params: { username } }),

  getSupervisors: () => http.get<any, any>('/api/auth/supervisors'),

  getMe: (userId: number) => http.get<any, any>(`/api/auth/me/${userId}`),

  updateProfile: (userId: number, data: Partial<UserInfo>) =>
    http.put<any, any>('/api/auth/profile', data, { params: { user_id: userId } }),

  changePassword: (data: { user_id: number; old_password: string; new_password: string }) =>
    http.post<any, any>('/api/auth/change-password', data),

  getAllUsers: () => http.get<any, any>('/api/auth/users'),

  updateUser: (userId: number, data: Partial<UserInfo & { password?: string }>) =>
    http.put<any, any>('/api/auth/user', data, { params: { user_id: userId } }),

  deleteUser: (userId: number) =>
    http.delete<any, any>('/api/auth/user', { params: { user_id: userId } })
}
