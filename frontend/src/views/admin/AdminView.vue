<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'
import { Users, Shield, Loader2, Check, X, RefreshCw } from 'lucide-vue-next'

const users = ref([])
const candidates = ref([])
const loading = ref(true)
const error = ref('')

onMounted(loadData)

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [usersRes, candidatesRes] = await Promise.all([
      api.get('/users/'),
      api.get('/candidates/'),
    ])
    users.value = usersRes.data
    candidates.value = candidatesRes.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

const ROLE_LABELS = { candidate: 'Кандидат', hr: 'HR', manager: 'Руководитель', admin: 'Администратор' }
const ROLE_COLORS = {
  candidate: 'bg-blue-400/10 text-blue-400',
  hr: 'bg-purple-400/10 text-purple-400',
  manager: 'bg-orange-400/10 text-orange-400',
  admin: 'bg-red-400/10 text-red-400',
}


</script>

<template>
  <div class="h-full flex flex-col bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <div class="p-4 md:p-8 pb-4 flex items-center justify-between">
      <div>
        <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
          <Shield class="w-7 h-7 text-brand-accent" />
          Панель администратора
        </h1>
        <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Управление пользователями и системой</p>
      </div>
      <button @click="loadData" class="p-2.5 rounded-xl border border-brand-light-border dark:border-brand-dark-border bg-brand-light-surface dark:bg-brand-dark-surface text-brand-light-secondary dark:text-brand-dark-secondary hover:text-brand-accent transition-all">
        <RefreshCw class="w-5 h-5" />
      </button>
    </div>

    <div class="flex-1 p-4 md:p-8 pt-0 overflow-y-auto space-y-8">
      <!-- Stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
          <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Всего пользователей</p>
          <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ users.length }}</p>
        </div>
        <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
          <p class="text-caption text-blue-400">Кандидатов</p>
          <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ users.filter(u => u.role === 'candidate').length }}</p>
        </div>
        <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
          <p class="text-caption text-purple-400">HR-специалистов</p>
          <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ users.filter(u => u.role === 'hr').length }}</p>
        </div>
        <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
          <p class="text-caption text-orange-400">Руководителей</p>
          <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ users.filter(u => u.role === 'manager').length }}</p>
        </div>
      </div>

      <!-- Users table -->
      <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border overflow-hidden">
        <div class="p-6 border-b border-brand-light-border dark:border-brand-dark-border flex items-center gap-3">
          <Users class="w-5 h-5 text-brand-accent" />
          <h2 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Пользователи</h2>
        </div>

        <div v-if="loading" class="flex items-center justify-center py-12">
          <Loader2 class="w-8 h-8 animate-spin text-brand-accent" />
        </div>

        <div v-else-if="error" class="p-6 text-center text-red-400">{{ error }}</div>

        <div v-else class="divide-y divide-brand-light-border dark:divide-brand-dark-border">
          <div
            v-for="user in users"
            :key="user.id"
            class="flex items-center justify-between px-6 py-4 hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated transition-colors"
          >
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-brand-accent/10 flex items-center justify-center">
                <span class="text-brand-accent text-sm font-bold">{{ (user.email || '?')[0].toUpperCase() }}</span>
              </div>
              <div>
                <p class="text-body font-medium text-brand-light-primary dark:text-brand-dark-primary">{{ user.email }}</p>
                <p class="text-micro text-brand-light-muted dark:text-brand-dark-muted">ID: {{ user.id }}</p>
              </div>
            </div>
            <span :class="['text-micro font-bold px-3 py-1 rounded-lg', ROLE_COLORS[user.role] || 'bg-gray-400/10 text-gray-400']">
              {{ ROLE_LABELS[user.role] || user.role }}
            </span>
          </div>
        </div>
      </div>

      <!-- Candidates summary -->
      <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border overflow-hidden">
        <div class="p-6 border-b border-brand-light-border dark:border-brand-dark-border">
          <h2 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Профили кандидатов ({{ candidates.length }})</h2>
        </div>
        <div class="divide-y divide-brand-light-border dark:divide-brand-dark-border">
          <div
            v-for="c in candidates"
            :key="c.id"
            class="flex items-center justify-between px-6 py-4"
          >
            <div>
              <p class="text-body font-medium text-brand-light-primary dark:text-brand-dark-primary">{{ c.full_name }}</p>
              <p class="text-micro text-brand-light-muted dark:text-brand-dark-muted">{{ c.email }}{{ c.desired_position ? ' · ' + c.desired_position : '' }}{{ c.city ? ' · ' + c.city : '' }}</p>
            </div>
            <a v-if="c.resume_url" :href="c.resume_url" target="_blank" class="text-micro font-bold text-brand-accent hover:underline">Резюме</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
