<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'
import {
  ClipboardList,
  Briefcase,
  Loader2,
  ExternalLink,
} from 'lucide-vue-next'

const myApps = ref([])
const vacancies = ref([])
const loading = ref(true)

const STATUS_LABELS = {
  new: 'Новый',
  screening: 'На рассмотрении',
  interview: 'Назначено HR-интервью',
  manager_interview: 'Интервью с руководителем',
  interview_done: 'Интервью проведено',
  awaiting_decision: 'Ожидает решения',
  reserve: 'Резерв',
  offer: 'Оффер',
  hired: 'Принят',
  rejected: 'Отказ',
  accepted: 'Принят',
}
const STATUS_COLORS = {
  new: 'bg-blue-400/10 text-blue-400',
  screening: 'bg-yellow-400/10 text-yellow-500',
  interview: 'bg-purple-400/10 text-purple-400',
  manager_interview: 'bg-indigo-400/10 text-indigo-400',
  interview_done: 'bg-cyan-400/10 text-cyan-500',
  awaiting_decision: 'bg-orange-400/10 text-orange-400',
  reserve: 'bg-teal-400/10 text-teal-500',
  offer: 'bg-emerald-400/10 text-emerald-500',
  hired: 'bg-green-500/10 text-green-500',
  rejected: 'bg-red-400/10 text-red-400',
  accepted: 'bg-green-600/10 text-green-600',
}
const STATUS_DOTS = {
  new: 'bg-blue-400',
  screening: 'bg-yellow-400',
  interview: 'bg-purple-400',
  manager_interview: 'bg-indigo-400',
  interview_done: 'bg-cyan-400',
  awaiting_decision: 'bg-orange-400',
  reserve: 'bg-teal-400',
  offer: 'bg-emerald-400',
  hired: 'bg-green-500',
  rejected: 'bg-red-400',
  accepted: 'bg-green-600',
}

onMounted(async () => {
  try {
    const [appsRes, vacRes] = await Promise.all([
      api.get('/applications/my'),
      api.get('/vacancies/'),
    ])
    myApps.value = appsRes.data
    vacancies.value = vacRes.data
  } catch {}
  loading.value = false
})

function vacancyFor(vacancyId) {
  return vacancies.value.find(v => v.id === vacancyId)
}

function vacancyTitle(vacancyId) {
  return vacancyFor(vacancyId)?.title || `Вакансия #${vacancyId}`
}

function formatDate(dt) {
  return new Date(dt).toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
}
</script>

<template>
  <div class="h-full flex flex-col bg-brand-light-base dark:bg-brand-dark-base antialiased">
      <div class="p-4 md:p-8 pb-4">
        <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
          <ClipboardList class="w-7 h-7 text-brand-accent" />
          Мои заявки
        </h1>
        <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Отслеживайте статус ваших откликов на вакансии</p>
      </div>

      <div class="flex-1 p-4 md:p-8 pt-0 overflow-y-auto">
        <div v-if="loading" class="flex items-center justify-center h-64">
          <Loader2 class="w-10 h-10 animate-spin text-brand-accent" />
        </div>

        <div v-else-if="myApps.length === 0" class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl px-5 py-12 flex flex-col items-center gap-3 text-center max-w-lg mx-auto">
          <ClipboardList class="w-12 h-12 text-brand-light-muted dark:text-brand-dark-muted" />
          <p class="text-body font-semibold text-brand-light-primary dark:text-brand-dark-primary">Заявок пока нет</p>
          <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Перейдите в раздел «Профиль» и откликнитесь на вакансию</p>
        </div>

        <div v-else class="max-w-3xl space-y-3">
          <div
            v-for="app in myApps"
            :key="app.id"
            class="group bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl p-5 flex items-center gap-4 hover:shadow-lg hover:shadow-brand-accent/5 transition-all"
          >
            <!-- Status dot -->
            <div class="flex flex-col items-center gap-1 shrink-0">
              <div :class="['w-3 h-3 rounded-full', STATUS_DOTS[app.status]]"></div>
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <h3 class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-sm truncate">
                    {{ vacancyTitle(app.vacancy_id) }}
                  </h3>
                  <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary mt-0.5">
                    Заявка #{{ app.id }}
                    <span v-if="app.created_at"> · {{ formatDate(app.created_at) }}</span>
                  </p>
                  <p v-if="vacancyFor(app.vacancy_id)?.description" class="text-caption text-brand-light-muted dark:text-brand-dark-muted mt-1 line-clamp-2">
                    {{ vacancyFor(app.vacancy_id).description }}
                  </p>
                </div>
                <span :class="['text-micro rounded-lg px-2.5 py-1 font-bold shrink-0 whitespace-nowrap', STATUS_COLORS[app.status]]">
                  {{ STATUS_LABELS[app.status] }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>
