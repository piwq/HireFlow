import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    // Only force logout on 401 from auth endpoints (expired/invalid token)
    // Don't redirect on 401 from regular endpoints — components handle their own errors
    if (err.response?.status === 401 && err.config?.url?.includes('/auth/')) {
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
