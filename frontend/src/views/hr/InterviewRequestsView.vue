<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/index.js'
import { ClipboardList, Loader2, Check, X, User, Clock } from 'lucide-vue-next'

const router = useRouter()
const requests = ref([])
const candidatesMap = ref({}) // candidate_id → profile
const usersMap = ref({})      // user_id → user
const loading = ref(true)
const updating = ref(null)

onMounted(load)

async function load() {
  loading.value = true
  try {
    const [reqRes, candidatesRes, usersRes] = await Promise.all([
      api.get('/interview-requests/'),
      api.get('/candidates/'),
      api.get('/users/'),
    ])
    requests.value = reqRes.data
    candidatesMap.value = Object.fromEntries(candidatesRes.data.map(c => [c.id, c]))
    usersMap.value = Object.fromEntries(usersRes.data.map(u => [u.id, u]))
  } finally {
    loading.value = false
  }
}

async function setStatus(req, status) {
  updating.value = req.id
  try {
    const res = await api.put(`/interview-requests/${req.id}/status`, { status })
    const idx = requests.value.findIndex(r => r.id === req.id)
    if (idx !== -1) requests.value[idx] = res.data
  } finally {
    updating.value = null
  }
}

const FORMAT_LABELS = {
  online: 'Онлайн',
  offline: 'Офлайн',
  phone: 'Телефон',
}

const STATUS_STYLE = {
  pending:  { label: 'Ожидает',  cls: 'bg-yellow-400/10 text-yellow-400 border-yellow-400/20' },
  accepted: { label: 'Принято',  cls: 'bg-green-500/10 text-green-500 border-green-500/20' },
  rejected: { label: 'Отклонено', cls: 'bg-red-400/10 text-red-400 border-red-400/20' },
}
</script>

<template>
  <div class="p-6 md:p-8 max-w-4xl mx-auto">
      <div class="flex items-center gap-3 mb-8">
        <ClipboardList class="w-7 h-7 text-brand-accent" />
        <div>
          <h1 class="text-2xl font-bold text-brand-light-primary dark:text-brand-dark-primary">Запросы на интервью</h1>
          <p class="text-sm text-brand-light-secondary dark:text-brand-dark-secondary mt-0.5">Запросы от руководителей на проведение встречи с кандидатами</p>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center py-20">
        <Loader2 class="w-10 h-10 animate-spin text-brand-accent" />
      </div>

      <div v-else-if="requests.length === 0" class="text-center py-20 text-brand-light-secondary dark:text-brand-dark-secondary">
        Нет запросов
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="req in requests"
          :key="req.id"
          class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl p-5"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-bold text-brand-light-primary dark:text-brand-dark-primary">
                  {{ candidatesMap[req.candidate_id]?.full_name || `Кандидат #${req.candidate_id}` }}
                </span>
                <button
                  @click="router.push(`/hr/candidates/${req.candidate_id}`)"
                  class="text-xs text-brand-accent hover:underline"
                >
                  Открыть карточку →
                </button>
                <span :class="['text-xs px-2 py-0.5 rounded-full border font-medium', STATUS_STYLE[req.status]?.cls]">
                  {{ STATUS_STYLE[req.status]?.label || req.status }}
                </span>
              </div>

              <div class="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-brand-light-secondary dark:text-brand-dark-secondary">
                <span v-if="candidatesMap[req.candidate_id]?.desired_position" class="text-brand-light-muted dark:text-brand-dark-muted">
                  {{ candidatesMap[req.candidate_id].desired_position }}
                </span>
                <span v-if="req.preferred_format" class="flex items-center gap-1">
                  Формат: <strong class="text-brand-light-primary dark:text-brand-dark-primary ml-1">{{ FORMAT_LABELS[req.preferred_format] || req.preferred_format }}</strong>
                </span>
                <span v-if="req.preferred_time" class="flex items-center gap-1">
                  <Clock class="w-3.5 h-3.5" /> {{ req.preferred_time }}
                </span>
                <span class="flex items-center gap-1">
                  <User class="w-3.5 h-3.5" />
                  {{ usersMap[req.manager_id]?.full_name || usersMap[req.manager_id]?.email || `Рук-ль #${req.manager_id}` }}
                </span>
              </div>

              <p v-if="req.comment" class="mt-2 text-sm text-brand-light-primary dark:text-brand-dark-primary bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-lg px-3 py-2">
                {{ req.comment }}
              </p>

              <p class="mt-2 text-xs text-brand-light-muted dark:text-brand-dark-muted">
                {{ new Date(req.created_at).toLocaleString('ru-RU') }}
              </p>
            </div>

            <div v-if="req.status === 'pending'" class="flex gap-2 shrink-0">
              <button
                @click="setStatus(req, 'accepted')"
                :disabled="updating === req.id"
                class="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/10 text-green-500 border border-green-500/20 rounded-xl text-sm font-medium hover:bg-green-500/20 transition-colors disabled:opacity-50"
              >
                <Check class="w-4 h-4" /> Принять
              </button>
              <button
                @click="setStatus(req, 'rejected')"
                :disabled="updating === req.id"
                class="flex items-center gap-1.5 px-3 py-1.5 bg-red-400/10 text-red-400 border border-red-400/20 rounded-xl text-sm font-medium hover:bg-red-400/20 transition-colors disabled:opacity-50"
              >
                <X class="w-4 h-4" /> Отклонить
              </button>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>
