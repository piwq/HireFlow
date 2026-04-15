import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/index.js'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const role = ref(localStorage.getItem('role') || null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    token.value = data.access_token
    role.value = data.role
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('role', data.role)
  }

  async function register(email, password, userRole) {
    const { data } = await api.post('/auth/register', { email, password, role: userRole })
    token.value = data.access_token
    role.value = data.role
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('role', data.role)
  }

  function logout() {
    token.value = null
    role.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
  }

  return { token, role, isAuthenticated, login, register, logout }
})
