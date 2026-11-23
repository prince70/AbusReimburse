import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  // 开发：vite 代理 /api → 8002；生产：同源直连（nginx → 8002 单端口，前端+API 同域）
  baseURL: '',
  timeout: 15000
})

http.interceptors.response.use(
  res => res.data,
  err => {
    const detail = err.response?.data?.detail
    const backendError = err.response?.data?.error
    if (err.response?.data) {
      console.error('API error response:', err.response.data)
    }
    const msg = [detail, backendError].filter(Boolean).join(': ') || err.message || '请求失败'
    ElMessage.error(msg)
    return Promise.reject(err)
  }
)

export default http
