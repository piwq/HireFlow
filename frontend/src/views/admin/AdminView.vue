<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api/index.js'
import { Users, Shield, Loader2, RefreshCw, Lock, Unlock, Trash2, BarChart3, ChevronDown } from 'lucide-vue-next'

const users = ref([])
const stats = ref(null)
const loading = ref(true)
const error = ref('')
const tab = ref('users') // 'users' | 'stats'
const roleDropdown = ref(null)

onMounted(loadData)

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [usersRes, statsRes] = await Promise.all([
      api.get('/admin/users'),
      api.get('/admin/stats'),
    ])
    users.value = usersRes.data
    stats.value = statsRes.data
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
const STATUS_LABELS = {
  new: 'Новый', screening: 'На рассмотрении', interview: 'HR-интервью',
  manager_interview: 'Интервью с рук.', interview_done: 'Проведено',
  awaiting_decision: 'Ожидает решения', reserve: 'Резерв', offer: 'Оффер',
  hired: 'Нанят', rejected: 'Отказ', accepted: 'Принят',
}
const roles = ['candidate', 'hr', 'manager', 'admin']

async function changeRole(user, newRole) {
  try {
    const res = await api.put(`/admin/users/${user.id}/role`, { role: newRole })
    Object.assign(user, res.data)
    roleDropdown.value = null
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

async function toggleBlock(user) {
  try {
    const res = await api.put(`/admin/users/${user.id}/block`, { is_blocked: !user.is_blocked })
    Object.assign(user, res.data)
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

async function deleteUser(user) {
  if (!confirm(`Удалить пользователя ${user.email}?`)) return
  try {
    await api.delete(`/admin/users/${user.id}`)
    users.value = users.value.filter(u => u.id !== user.id)
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

const blockedCount = computed(() => users.value.filter(u => u.is_blocked).length)
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

    <!-- Tabs -->
    <div class="px-4 md:px-8 flex gap-2">
      <button @click="tab = 'users'" :class="['px-4 py-2 rounded-xl text-sm font-bold transition-all', tab === 'users' ? 'bg-brand-accent text-white' : 'bg-brand-light-surface dark:bg-brand-dark-surface text-brand-light-secondary dark:text-brand-dark-secondary border border-brand-light-border dark:border-brand-dark-border']">
        <Users class="w-4 h-4 inline mr-1.5" />Пользователи
      </button>
      <button @click="tab = 'stats'" :class="['px-4 py-2 rounded-xl text-sm font-bold transition-all', tab === 'stats' ? 'bg-brand-accent text-white' : 'bg-brand-light-surface dark:bg-brand-dark-surface text-brand-light-secondary dark:text-brand-dark-secondary border border-brand-light-border dark:border-brand-dark-border']">
        <BarChart3 class="w-4 h-4 inline mr-1.5" />Статистика
      </button>
    </div>

    <div class="flex-1 p-4 md:p-8 pt-4 overflow-y-auto space-y-6">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <Loader2 class="w-8 h-8 animate-spin text-brand-accent" />
      </div>
      <div v-else-if="error" class="p-6 text-center text-red-400">{{ error }}</div>

      <!-- Users Tab -->
      <template v-else-if="tab === 'users'">
        <!-- Quick stats -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Всего</p>
            <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ users.length }}</p>
          </div>
          <div v-for="r in roles" :key="r" class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <p :class="['text-caption', ROLE_COLORS[r].split(' ')[1]]">{{ ROLE_LABELS[r] }}</p>
            <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ users.filter(u => u.role === r).length }}</p>
          </div>
        </div>

        <!-- Users table -->
        <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border overflow-hidden">
          <div class="p-6 border-b border-brand-light-border dark:border-brand-dark-border flex items-center justify-between">
            <div class="flex items-center gap-3">
              <Users class="w-5 h-5 text-brand-accent" />
              <h2 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Пользователи</h2>
            </div>
            <span v-if="blockedCount > 0" class="text-micro font-bold px-3 py-1 rounded-lg bg-red-400/10 text-red-400">
              {{ blockedCount }} заблокировано
            </span>
          </div>

          <div class="divide-y divide-brand-light-border dark:divide-brand-dark-border">
            <div
              v-for="user in users"
              :key="user.id"
              :class="['flex items-center justify-between px-6 py-4 transition-colors', user.is_blocked ? 'opacity-50 bg-red-500/5' : 'hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated']"
            >
              <div class="flex items-center gap-3">
                <div :class="['w-9 h-9 rounded-xl flex items-center justify-center', user.is_blocked ? 'bg-red-400/10' : 'bg-brand-accent/10']">
                  <span :class="['text-sm font-bold', user.is_blocked ? 'text-red-400' : 'text-brand-accent']">{{ (user.email || '?')[0].toUpperCase() }}</span>
                </div>
                <div>
                  <p class="text-body font-medium text-brand-light-primary dark:text-brand-dark-primary">
                    {{ user.email }}
                    <span v-if="user.is_blocked" class="text-micro text-red-400 ml-2">🔒 заблокирован</span>
                  </p>
                  <p class="text-micro text-brand-light-muted dark:text-brand-dark-muted">ID: {{ user.id }}</p>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <!-- Role dropdown -->
                <div class="relative">
                  <button
                    @click.stop="roleDropdown = roleDropdown === user.id ? null : user.id"
                    :class="['text-micro font-bold px-3 py-1.5 rounded-lg flex items-center gap-1 cursor-pointer transition-all hover:opacity-80', ROLE_COLORS[user.role] || 'bg-gray-400/10 text-gray-400']"
                  >
                    {{ ROLE_LABELS[user.role] || user.role }}
                    <ChevronDown class="w-3 h-3" />
                  </button>
                  <div v-if="roleDropdown === user.id" class="absolute right-0 mt-1 w-44 bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl shadow-xl z-20 py-1">
                    <button
                      v-for="r in roles"
                      :key="r"
                      @click="changeRole(user, r)"
                      :class="['w-full text-left px-4 py-2 text-sm transition-colors', user.role === r ? 'text-brand-accent font-bold' : 'text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated']"
                    >
                      {{ ROLE_LABELS[r] }}
                    </button>
                  </div>
                </div>

                <!-- Block/Unblock -->
                <button
                  @click="toggleBlock(user)"
                  :class="['p-2 rounded-lg transition-all', user.is_blocked ? 'text-green-400 hover:bg-green-400/10' : 'text-yellow-400 hover:bg-yellow-400/10']"
                  :title="user.is_blocked ? 'Разблокировать' : 'Заблокировать'"
                >
                  <Unlock v-if="user.is_blocked" class="w-4 h-4" />
                  <Lock v-else class="w-4 h-4" />
                </button>

                <!-- Delete -->
                <button @click="deleteUser(user)" class="p-2 rounded-lg text-red-400 hover:bg-red-400/10 transition-all" title="Удалить">
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Stats Tab -->
      <template v-else-if="tab === 'stats' && stats">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Пользователей</p>
            <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ stats.total_users }}</p>
          </div>
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <p class="text-caption text-blue-400">Кандидатов</p>
            <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ stats.total_candidates }}</p>
          </div>
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <p class="text-caption text-purple-400">Заявок</p>
            <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ stats.total_applications }}</p>
          </div>
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <p class="text-caption text-orange-400">Интервью</p>
            <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ stats.total_interviews }}</p>
          </div>
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <p class="text-caption text-cyan-400">Отзывов</p>
            <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ stats.total_feedbacks }}</p>
          </div>
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <p class="text-caption text-red-400">Заблокировано</p>
            <p class="text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ stats.blocked_users }}</p>
          </div>
        </div>

        <!-- Status distribution -->
        <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6">
          <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary mb-4">Распределение заявок по статусам</h3>
          <div class="space-y-3">
            <div v-for="(count, status) in stats.status_counts" :key="status" class="flex items-center gap-3">
              <span class="text-sm text-brand-light-secondary dark:text-brand-dark-secondary w-40 shrink-0">{{ STATUS_LABELS[status] || status }}</span>
              <div class="flex-1 h-6 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-full overflow-hidden">
                <div class="h-full bg-brand-accent/60 rounded-full transition-all" :style="{ width: Math.max(4, (count / stats.total_applications * 100)) + '%' }"></div>
              </div>
              <span class="text-sm font-bold text-brand-light-primary dark:text-brand-dark-primary w-10 text-right">{{ count }}</span>
            </div>
          </div>
        </div>

        <!-- Role distribution -->
        <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6">
          <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary mb-4">Пользователи по ролям</h3>
          <div class="space-y-3">
            <div v-for="(count, role) in stats.role_counts" :key="role" class="flex items-center gap-3">
              <span :class="['text-sm w-40 shrink-0', ROLE_COLORS[role]?.split(' ')[1] || 'text-brand-light-secondary dark:text-brand-dark-secondary']">{{ ROLE_LABELS[role] || role }}</span>
              <div class="flex-1 h-6 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-full overflow-hidden">
                <div class="h-full bg-brand-accent/60 rounded-full transition-all" :style="{ width: Math.max(4, (count / stats.total_users * 100)) + '%' }"></div>
              </div>
              <span class="text-sm font-bold text-brand-light-primary dark:text-brand-dark-primary w-10 text-right">{{ count }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
