<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/index.js'
import {
  Video,
  Calendar,
  Clock,
  Loader2,
  MapPin,
  MessageSquare,
  CheckCircle,
  XCircle,
} from 'lucide-vue-next'

const router = useRouter()
const myInterviews = ref([])
const myApps = ref([])
const vacancies = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [interviewsRes, appsRes, vacRes] = await Promise.all([
      api.get('/interviews/my'),
      api.get('/applications/my'),
      api.get('/vacancies/'),
    ])
    myInterviews.value = interviewsRes.data
    myApps.value = appsRes.data
    vacancies.value = vacRes.data
  } catch {}
  loading.value = false
})

function interviewVacancyTitle(interview) {
  const app = myApps.value.find(a => a.id === interview.application_id)
  return app ? vacancies.value.find(v => v.id === app.vacancy_id)?.title || `Вакансия` : `Заявка #${interview.application_id}`
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', {
    day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit',
  })
}

function isUpcoming(dt) {
  return new Date(dt) > new Date()
}

const FORMAT_LABELS = { online: 'Онлайн', offline: 'Офлайн', phone: 'Телефон' }
const INVITATION_LABELS = { pending: 'Ожидает подтверждения', confirmed: 'Подтверждено', declined: 'Отклонено' }
const INVITATION_COLORS = { pending: 'bg-yellow-400/10 text-yellow-400', confirmed: 'bg-green-500/10 text-green-500', declined: 'bg-red-400/10 text-red-400' }

async function updateInvitation(interview, status) {
  try {
    const res = await api.put(`/interviews/${interview.id}/invitation`, { status })
    interview.invitation_status = res.data.invitation_status
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}
</script>

<template>
  <div class="h-full flex flex-col bg-brand-light-base dark:bg-brand-dark-base antialiased">
      <div class="p-4 md:p-8 pb-4">
        <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
          <Video class="w-7 h-7 text-brand-accent" />
          Собеседования
        </h1>
        <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Предстоящие и прошедшие видеовстречи</p>
      </div>

      <div class="flex-1 p-4 md:p-8 pt-0 overflow-y-auto">
        <div v-if="loading" class="flex items-center justify-center h-64">
          <Loader2 class="w-10 h-10 animate-spin text-brand-accent" />
        </div>

        <div v-else-if="myInterviews.length === 0" class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl px-5 py-12 flex flex-col items-center gap-3 text-center max-w-lg mx-auto">
          <Video class="w-12 h-12 text-brand-light-muted dark:text-brand-dark-muted" />
          <p class="text-body font-semibold text-brand-light-primary dark:text-brand-dark-primary">Собеседований пока нет</p>
          <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Собеседования появятся здесь после назначения HR-менеджером</p>
        </div>

        <div v-else class="max-w-3xl space-y-3">
          <!-- Upcoming -->
          <template v-for="interview in myInterviews" :key="interview.id">
            <div
              class="group bg-brand-light-surface dark:bg-brand-dark-surface border rounded-2xl p-5 flex items-center justify-between gap-4 hover:shadow-lg hover:shadow-brand-accent/5 transition-all"
              :class="isUpcoming(interview.scheduled_at)
                ? 'border-brand-status-interview/40'
                : 'border-brand-light-border dark:border-brand-dark-border'"
            >
              <div class="flex items-center gap-4 min-w-0">
                <div
                  class="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
                  :class="isUpcoming(interview.scheduled_at)
                    ? 'bg-brand-status-interview/10 border border-brand-status-interview/20'
                    : 'bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border'"
                >
                  <Calendar
                    class="w-5 h-5"
                    :class="isUpcoming(interview.scheduled_at) ? 'text-brand-status-interview' : 'text-brand-light-muted dark:text-brand-dark-muted'"
                  />
                </div>
                <div class="min-w-0">
                  <div class="flex items-center gap-2">
                    <p class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-sm truncate">
                      {{ interviewVacancyTitle(interview) }}
                    </p>
                    <span
                      v-if="isUpcoming(interview.scheduled_at)"
                      class="text-micro bg-brand-status-interview/10 text-brand-status-interview px-2 py-0.5 rounded-md font-bold shrink-0"
                    >
                      Предстоящее
                    </span>
                    <span
                      v-else
                      class="text-micro bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-muted dark:text-brand-dark-muted px-2 py-0.5 rounded-md font-bold shrink-0"
                    >
                      Завершено
                    </span>
                  </div>
                  <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary mt-1 flex items-center gap-1">
                    <Clock class="w-3 h-3" />
                    {{ formatDate(interview.scheduled_at) }}
                    <span v-if="interview.format" class="ml-2 px-1.5 py-0.5 rounded bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-muted dark:text-brand-dark-muted text-micro">
                      {{ FORMAT_LABELS[interview.format] || interview.format }}
                    </span>
                  </p>
                  <p v-if="interview.location" class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary mt-0.5 flex items-center gap-1">
                    <MapPin class="w-3 h-3 shrink-0" />
                    {{ interview.location }}
                  </p>
                  <p v-if="interview.comment" class="text-caption text-brand-light-muted dark:text-brand-dark-muted mt-0.5 flex items-start gap-1">
                    <MessageSquare class="w-3 h-3 shrink-0 mt-0.5" />
                    {{ interview.comment }}
                  </p>
                </div>
              </div>

              <button
                v-if="isUpcoming(interview.scheduled_at)"
                @click="router.push(`/call/${interview.room_code}`)"
                class="flex items-center gap-2 px-5 py-2.5 bg-brand-status-interview hover:bg-brand-status-interview/80 text-white rounded-xl text-sm font-bold transition-all shrink-0 shadow-lg shadow-brand-status-interview/20 active:scale-95"
              >
                <Video class="w-4 h-4" />
                Войти
              </button>

              <div class="flex flex-col items-end gap-2 shrink-0">
                <!-- Invitation status -->
                <span v-if="interview.invitation_status" :class="['text-micro font-bold px-2.5 py-1 rounded-lg', INVITATION_COLORS[interview.invitation_status] || 'bg-gray-400/10 text-gray-400']">
                  {{ INVITATION_LABELS[interview.invitation_status] || interview.invitation_status }}
                </span>
                <!-- Confirm/Decline buttons -->
                <div v-if="isUpcoming(interview.scheduled_at) && (!interview.invitation_status || interview.invitation_status === 'pending')" class="flex gap-1.5">
                  <button @click="updateInvitation(interview, 'confirmed')" class="flex items-center gap-1 px-3 py-1.5 bg-green-500/10 text-green-500 hover:bg-green-500/20 rounded-lg text-xs font-bold transition-all">
                    <CheckCircle class="w-3.5 h-3.5" /> Подтвердить
                  </button>
                  <button @click="updateInvitation(interview, 'declined')" class="flex items-center gap-1 px-3 py-1.5 bg-red-400/10 text-red-400 hover:bg-red-400/20 rounded-lg text-xs font-bold transition-all">
                    <XCircle class="w-3.5 h-3.5" /> Отклонить
                  </button>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
  </div>
</template>
