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
  screening: 'Скрининг',
  interview: 'Интервью',
  hired: 'Нанят',
  rejected: 'Отказ',
}
const STATUS_COLORS = {
  new: 'bg-brand-status-new/10 text-brand-status-new',
  screening: 'bg-brand-status-screening/10 text-brand-status-screening',
  interview: 'bg-brand-status-interview/10 text-brand-status-interview',
  hired: 'bg-brand-status-hired/10 text-brand-status-hired',
  rejected: 'bg-brand-status-rejected/10 text-brand-status-rejected',
}
const STATUS_DOTS = {
  new: 'bg-brand-status-new',
  screening: 'bg-brand-status-screening',
  interview: 'bg-brand-status-interview',
  hired: 'bg-brand-status-hired',
  rejected: 'bg-brand-status-rejected',
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

function vacancyTitle(vacancyId) {
  return vacancies.value.find(v => v.id === vacancyId)?.title || `Вакансия #${vacancyId}`
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
