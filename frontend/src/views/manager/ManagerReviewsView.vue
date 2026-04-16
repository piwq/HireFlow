<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import api from '@/api/index.js'
import {
  FileText,
  Loader2,
  Calendar,
  MessageSquare,
  Clock,
  ThumbsUp,
  ThumbsDown,
  Star,
} from 'lucide-vue-next'

const auth = useAuthStore()
const currentUserId = auth.userId

const allFeedbacks = ref([])
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
    allFeedbacks.value = fbRes.data
    interviews.value = intRes.data
    applications.value = appRes.data
    candidates.value = candRes.data
  } finally {
    loading.value = false
  }
}

// Only show this manager's own feedbacks
const feedbacks = computed(() =>
  allFeedbacks.value.filter(fb => fb.manager_id === currentUserId)
)

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

function candidateForFeedback(fb) {
  return candidateForApplication(applicationForInterview(interviewForFeedback(fb)))
}

function initials(name) {
  if (!name) return '?'
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const RECOMMENDATION_STYLE = {
  recommend:    { label: 'Рекомендовать',       cls: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' },
  reserve:      { label: 'Резерв',              cls: 'bg-teal-500/10 text-teal-500 border-teal-500/20' },
  reject:       { label: 'Отказать',            cls: 'bg-red-400/10 text-red-400 border-red-400/20' },
  re_interview: { label: 'Повторное интервью',  cls: 'bg-orange-400/10 text-orange-400 border-orange-400/20' },
}
</script>

<template>
  <div class="bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <!-- Header -->
    <div class="p-4 md:p-8 pb-4">
      <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
        <FileText class="w-7 h-7 text-brand-accent" />
        Мои отзывы
      </h1>
      <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">
        История оставленных вами оценок кандидатов
      </p>
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

      <div v-else class="space-y-6 max-w-3xl">
        <div
          v-for="fb in feedbacks"
          :key="fb.id"
          class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl overflow-hidden"
        >
          <!-- Header row -->
          <div class="p-5 flex items-start justify-between gap-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center shrink-0">
                <span class="text-brand-accent text-sm font-bold">{{ initials(candidateForFeedback(fb)?.full_name) }}</span>
              </div>
              <div>
                <p class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-sm">
                  {{ candidateForFeedback(fb)?.full_name || 'Кандидат' }}
                </p>
                <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary flex items-center gap-1 mt-0.5">
                  <Calendar class="w-3 h-3" />
                  Интервью {{ interviewForFeedback(fb) ? formatDate(interviewForFeedback(fb).scheduled_at) : '—' }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0 flex-col items-end">
              <div class="flex items-center gap-1 text-caption text-brand-light-muted dark:text-brand-dark-muted">
                <Clock class="w-3.5 h-3.5" />
                {{ formatDate(fb.created_at) }}
              </div>
              <span
                v-if="fb.recommendation && RECOMMENDATION_STYLE[fb.recommendation]"
                :class="['text-xs px-2.5 py-0.5 rounded-full border font-medium', RECOMMENDATION_STYLE[fb.recommendation].cls]"
              >
                {{ RECOMMENDATION_STYLE[fb.recommendation].label }}
              </span>
            </div>
          </div>

          <!-- Scores -->
          <div
            v-if="fb.score_overall || fb.score_technical || fb.score_communication || fb.score_fit"
            class="px-5 pb-4 grid grid-cols-2 sm:grid-cols-4 gap-3"
          >
            <div v-for="item in [
              { label: 'Общая', val: fb.score_overall },
              { label: 'Проф.', val: fb.score_technical },
              { label: 'Коммун.', val: fb.score_communication },
              { label: 'Соотв.', val: fb.score_fit },
            ]" :key="item.label" v-if="item.val">
              <div class="bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-xl p-3 text-center">
                <p class="text-micro text-brand-light-muted dark:text-brand-dark-muted mb-1">{{ item.label }}</p>
                <div class="flex items-center justify-center gap-0.5">
                  <Star
                    v-for="n in 5" :key="n"
                    class="w-3 h-3"
                    :class="n <= item.val ? 'text-yellow-400 fill-yellow-400' : 'text-brand-light-border dark:text-brand-dark-border'"
                  />
                </div>
                <p class="text-xs font-bold text-brand-light-primary dark:text-brand-dark-primary mt-1">{{ item.val }}/5</p>
              </div>
            </div>
          </div>

          <!-- Strengths / Weaknesses -->
          <div v-if="fb.strengths || fb.weaknesses" class="px-5 pb-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-if="fb.strengths" class="bg-emerald-500/5 border border-emerald-500/15 rounded-xl p-3">
              <p class="text-caption font-bold text-emerald-500 flex items-center gap-1 mb-1.5">
                <ThumbsUp class="w-3.5 h-3.5" /> Сильные стороны
              </p>
              <p class="text-caption text-brand-light-primary dark:text-brand-dark-primary whitespace-pre-wrap">{{ fb.strengths }}</p>
            </div>
            <div v-if="fb.weaknesses" class="bg-red-400/5 border border-red-400/15 rounded-xl p-3">
              <p class="text-caption font-bold text-red-400 flex items-center gap-1 mb-1.5">
                <ThumbsDown class="w-3.5 h-3.5" /> Слабые стороны
              </p>
              <p class="text-caption text-brand-light-primary dark:text-brand-dark-primary whitespace-pre-wrap">{{ fb.weaknesses }}</p>
            </div>
          </div>

          <!-- Comment -->
          <div class="px-5 pb-5 border-t border-brand-light-border dark:border-brand-dark-border pt-4">
            <p class="text-body text-brand-light-primary dark:text-brand-dark-primary leading-relaxed whitespace-pre-wrap">{{ fb.text }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
