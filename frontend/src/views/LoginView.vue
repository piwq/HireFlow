<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useThemeStore } from '@/stores/theme.js'
import { Mail, Lock, Sun, Moon, Briefcase, AlertCircle, Loader2 } from 'lucide-vue-next'

const auth = useAuthStore()
const theme = useThemeStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Заполните все поля'
    return
  }
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push(`/${auth.role}`)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Неверный email или пароль'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-brand-light-base dark:bg-brand-dark-base flex items-center justify-center p-4 antialiased font-sans">
    <!-- Theme toggle top right -->
    <button
      @click="theme.toggle()"
      class="fixed top-6 right-6 w-10 h-10 rounded-xl bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border flex items-center justify-center text-brand-light-secondary dark:text-brand-dark-secondary hover:text-brand-light-primary dark:hover:text-brand-dark-primary transition-all duration-200 shadow-sm"
    >
      <Sun v-if="theme.dark" class="w-5 h-5" />
      <Moon v-else class="w-5 h-5" />
    </button>

    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="flex items-center justify-center gap-3 mb-10">
        <div class="w-12 h-12 rounded-2xl bg-brand-accent flex items-center justify-center shadow-xl shadow-brand-accent/30">
          <Briefcase class="w-6 h-6 text-white" />
        </div>
        <h1 class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-3xl tracking-tight">HireFlow</h1>
      </div>

      <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border shadow-2xl shadow-brand-accent/5 p-10">
        <div class="mb-8">
          <h2 class="text-display text-brand-light-primary dark:text-brand-dark-primary mb-2">С возвращением</h2>
          <p class="text-body text-brand-light-secondary dark:text-brand-dark-secondary">Войдите в систему управления персоналом</p>
        </div>

        <form @submit.prevent="submit" class="space-y-6">
          <div class="space-y-2">
            <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Email</label>
            <div class="relative group">
              <Mail class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted group-focus-within:text-brand-accent transition-colors" />
              <input
                v-model="email"
                type="email"
                placeholder="name@company.com"
                class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-11 pr-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent dark:focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/10 transition-all"
              />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Пароль</label>
            <div class="relative group">
              <Lock class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted group-focus-within:text-brand-accent transition-colors" />
              <input
                v-model="password"
                type="password"
                placeholder="••••••••"
                class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-11 pr-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent dark:focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/10 transition-all"
              />
            </div>
          </div>

          <div v-if="error" class="flex items-start gap-3 bg-red-500/5 border border-red-500/20 rounded-xl p-4">
            <AlertCircle class="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <p class="text-caption text-red-500">{{ error }}</p>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-brand-accent hover:bg-brand-accent-hover active:scale-[0.98] disabled:opacity-60 text-white rounded-xl py-3.5 text-body font-bold transition-all shadow-lg shadow-brand-accent/25 flex items-center justify-center gap-2"
          >
            <Loader2 v-if="loading" class="w-5 h-5 animate-spin" />
            {{ loading ? 'Авторизация...' : 'Войти в систему' }}
          </button>
        </form>

        <div class="mt-8 pt-8 border-t border-brand-light-border dark:border-brand-dark-border text-center">
          <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">
            У вас еще нет аккаунта?
            <RouterLink to="/register" class="text-brand-accent font-semibold hover:text-brand-accent-hover transition-colors ml-1">
              Регистрация профиля
            </RouterLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
