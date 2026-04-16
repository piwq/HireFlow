import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/index.js'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const role = ref(localStorage.getItem('role') || null)
  const userId = ref(parseInt(localStorage.getItem('user_id')) || null)
  const email = ref(localStorage.getItem('email') || null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(loginEmail, password) {
    const { data } = await api.post('/auth/login', { email: loginEmail, password })
    token.value = data.access_token
    role.value = data.role
    userId.value = data.user_id
    email.value = data.email
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('role', data.role)
    localStorage.setItem('user_id', data.user_id)
    localStorage.setItem('email', data.email)
  }

  async function register(registerEmail, password, userRole) {
    const { data } = await api.post('/auth/register', { email: registerEmail, password, role: userRole })
    token.value = data.access_token
    role.value = data.role
    userId.value = data.user_id
    email.value = data.email
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('role', data.role)
    localStorage.setItem('user_id', data.user_id)
    localStorage.setItem('email', data.email)
  }

  function logout() {
    token.value = null
    role.value = null
    userId.value = null
    email.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('user_id')
    localStorage.removeItem('email')
  }

  return { token, role, userId, email, isAuthenticated, login, register, logout }
})
