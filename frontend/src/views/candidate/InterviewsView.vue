<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/index.js'
import {
  Video,
  Calendar,
  Clock,
  Loader2,
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
            </div>
          </template>
        </div>
      </div>
  </div>
</template>
