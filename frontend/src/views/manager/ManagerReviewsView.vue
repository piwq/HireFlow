<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'
import {
  FileText,
  Loader2,
  Calendar,
  MessageSquare,
  Clock,
} from 'lucide-vue-next'

const feedbacks = ref([])
const interviews = ref([])
const applications = ref([])
const candidates = ref([])
const loading = ref(true)

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const [fbRes, intRes, appRes, candRes] = await Promise.all([
      api.get('/feedbacks/'),
      api.get('/interviews/'),
      api.get('/applications/'),
      api.get('/candidates/'),
    ])
    feedbacks.value = fbRes.data
    interviews.value = intRes.data
    applications.value = appRes.data
    candidates.value = candRes.data
  } finally {
    loading.value = false
  }
}

function interviewForFeedback(fb) {
  return interviews.value.find(i => i.id === fb.interview_id)
}

function applicationForInterview(interview) {
  if (!interview) return null
  return applications.value.find(a => a.id === interview.application_id)
}

function candidateForApplication(app) {
  if (!app) return null
  return candidates.value.find(c => c.id === app.candidate_id)
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}
</script>

<template>
  <div class="bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <!-- Header -->
    <div class="p-4 md:p-8 pb-4">
      <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
        <FileText class="w-7 h-7 text-brand-accent" />
        Отзывы
      </h1>
      <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">История оставленных оценок кандидатов</p>
    </div>

    <!-- Content -->
    <div class="p-4 md:p-8 pt-4">
      <div v-if="loading" class="flex items-center justify-center h-64">
        <Loader2 class="w-10 h-10 animate-spin text-brand-accent" />
      </div>

      <div v-else-if="feedbacks.length === 0" class="flex flex-col items-center justify-center h-64 gap-4 text-center">
        <div class="w-16 h-16 rounded-2xl bg-brand-light-elevated dark:bg-brand-dark-elevated flex items-center justify-center">
          <MessageSquare class="w-8 h-8 text-brand-light-muted dark:text-brand-dark-muted" />
        </div>
        <div>
          <p class="text-body font-semibold text-brand-light-primary dark:text-brand-dark-primary">Отзывов пока нет</p>
          <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary mt-1">После проведения интервью оставьте оценку кандидату</p>
        </div>
      </div>

      <div v-else class="space-y-4 max-w-3xl">
        <div
          v-for="fb in feedbacks"
          :key="fb.id"
          class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl p-6"
        >
          <!-- Candidate + interview info -->
          <div class="flex items-start justify-between gap-4 mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center shrink-0">
                <span class="text-brand-accent text-sm font-bold">
                  {{
                    (() => {
                      const name = candidateForApplication(applicationForInterview(interviewForFeedback(fb)))?.full_name
                      if (!name) return '?'
                      return name.split(' ').slice(0,2).map(w => w[0]).join('').toUpperCase()
                    })()
                  }}
                </span>
              </div>
              <div>
                <p class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-sm">
                  {{ candidateForApplication(applicationForInterview(interviewForFeedback(fb)))?.full_name || 'Кандидат' }}
                </p>
                <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary flex items-center gap-1 mt-0.5">
                  <Calendar class="w-3 h-3" />
                  Интервью {{ interviewForFeedback(fb) ? formatDate(interviewForFeedback(fb).scheduled_at) : '—' }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-1.5 text-caption text-brand-light-muted dark:text-brand-dark-muted shrink-0">
              <Clock class="w-3.5 h-3.5" />
              {{ formatDate(fb.created_at) }}
            </div>
          </div>

          <!-- Feedback text -->
          <div class="bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-xl p-4">
            <p class="text-body text-brand-light-primary dark:text-brand-dark-primary leading-relaxed whitespace-pre-wrap">{{ fb.text }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
