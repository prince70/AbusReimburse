import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
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
