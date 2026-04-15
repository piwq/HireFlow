<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const role = ref('candidate')
const error = ref('')
const loading = ref(false)

const roles = [
  { value: 'candidate', label: 'Кандидат' },
  { value: 'hr', label: 'HR-специалист' },
  { value: 'manager', label: 'Руководитель' },
]

async function submit() {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Заполните все поля'
    return
  }
  if (password.value.length < 6) {
    error.value = 'Пароль минимум 6 символов'
    return
  }
  loading.value = true
  try {
    await auth.register(email.value, password.value, role.value)
    router.push(`/${auth.role}`)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="bg-white rounded-2xl shadow-md p-8 w-full max-w-sm">
      <h1 class="text-2xl font-bold text-gray-800 mb-6 text-center">Регистрация</h1>

      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="example@mail.ru"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
          <input
            v-model="password"
            type="password"
            placeholder="Минимум 6 символов"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Роль</label>
          <select
            v-model="role"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</option>
          </select>
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white rounded-lg py-2 font-medium hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {{ loading ? 'Регистрируем...' : 'Зарегистрироваться' }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-500 mt-4">
        Уже есть аккаунт?
        <RouterLink to="/login" class="text-blue-600 hover:underline">Войти</RouterLink>
      </p>
    </div>
  </div>
</template>
