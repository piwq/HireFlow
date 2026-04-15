<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useThemeStore } from '@/stores/theme.js'

const auth = useAuthStore()
const theme = useThemeStore()
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
  <div class="min-h-screen bg-slate-50 dark:bg-[#0D0F1A] flex items-center justify-center p-4">
    <!-- Theme toggle -->
    <button
      @click="theme.toggle()"
      class="fixed top-4 right-4 w-9 h-9 rounded-lg bg-white dark:bg-[#151827] border border-slate-200 dark:border-[#2A2F4A] flex items-center justify-center text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition shadow-sm"
    >
      {{ theme.dark ? '☀️' : '🌙' }}
    </button>

    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="flex items-center justify-center gap-3 mb-8">
        <div class="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
          <span class="text-white font-bold text-lg">H</span>
        </div>
        <span class="font-bold text-slate-900 dark:text-slate-100 text-2xl tracking-tight">HireFlow</span>
      </div>

      <div class="bg-white dark:bg-[#151827] rounded-2xl border border-slate-200 dark:border-[#2A2F4A] shadow-xl shadow-slate-200/60 dark:shadow-black/20 p-8">
        <h1 class="text-xl font-bold text-slate-900 dark:text-slate-100 mb-1">Создать аккаунт</h1>
        <p class="text-slate-500 dark:text-slate-400 text-sm mb-6">Заполните данные для регистрации</p>

        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Email</label>
            <input
              v-model="email"
              type="email"
              placeholder="example@mail.ru"
              class="w-full bg-slate-50 dark:bg-[#1E2235] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 focus:outline-none focus:border-indigo-500 dark:focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Пароль</label>
            <input
              v-model="password"
              type="password"
              placeholder="Минимум 6 символов"
              class="w-full bg-slate-50 dark:bg-[#1E2235] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 focus:outline-none focus:border-indigo-500 dark:focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Роль</label>
            <select
              v-model="role"
              class="w-full bg-slate-50 dark:bg-[#1E2235] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-indigo-500 dark:focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition"
            >
              <option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</option>
            </select>
          </div>

          <div v-if="error" class="flex items-center gap-2 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-lg px-3.5 py-2.5">
            <p class="text-red-600 dark:text-red-400 text-sm">{{ error }}</p>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 disabled:opacity-60 text-white rounded-lg py-2.5 text-sm font-semibold transition-all shadow-md shadow-indigo-500/25 hover:shadow-lg hover:shadow-indigo-500/30 mt-2"
          >
            {{ loading ? 'Регистрируем...' : 'Зарегистрироваться' }}
          </button>
        </form>

        <p class="text-center text-sm text-slate-500 dark:text-slate-400 mt-5">
          Уже есть аккаунт?
          <RouterLink to="/login" class="text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
            Войти
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
