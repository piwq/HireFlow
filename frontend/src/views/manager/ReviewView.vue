<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import api from '@/api/index.js'
import {
  Video,
  MessageSquare,
  Calendar,
  Mail,
  Loader2,
  Check,
  X,
  FileText,
  Star,
  ThumbsUp,
  ThumbsDown,
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()
const currentUserId = auth.userId

const interviews = ref([])
const candidates = ref([])
const applications = ref([])
const submitted = ref({})
const loading = ref(false)

// Per-interview feedback state
const feedbacks = ref({})

const showSchedule = ref(false)
const scheduleApp = ref(null)
const scheduleDate = ref('')
const scheduleTime = ref('')
const scheduleError = ref('')
const scheduleLoading = ref(false)

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const [ivRes, appsRes, candidatesRes] = await Promise.all([
      api.get('/interviews/'),
      api.get('/applications/'),
      api.get('/candidates/'),
    ])
    applications.value = appsRes.data
    candidates.value = candidatesRes.data

    // Only show interviews that are assigned to this manager OR belong to manager_interview apps
    const managerAppIds = new Set(
      appsRes.data
        .filter(a => a.status === 'manager_interview' || a.status === 'interview_done')
        .map(a => a.id)
    )
    interviews.value = ivRes.data.filter(
      iv => iv.manager_id === currentUserId || managerAppIds.has(iv.application_id)
    )

    // Init feedback state per interview
    for (const iv of interviews.value) {
      if (!feedbacks.value[iv.id]) {
        feedbacks.value[iv.id] = {
          text: '',
          score_overall: 0,
          score_technical: 0,
          score_communication: 0,
          score_fit: 0,
          strengths: '',
          weaknesses: '',
          recommendation: '',
        }
      }
    }
  } finally {
    loading.value = false
  }
}

const pendingApps = computed(() => {
  const scheduledAppIds = new Set(interviews.value.map((i) => i.application_id))
  // Manager sees apps that are at manager_interview stage but not yet scheduled
  return applications.value.filter(
    (a) => a.status === 'manager_interview' && !scheduledAppIds.has(a.id)
  )
})

function candidateForApp(app) {
  return candidates.value.find((c) => c.id === app.candidate_id)
}

function candidateForInterview(interview) {
  const app = applications.value.find((a) => a.id === interview.application_id)
  if (!app) return null
  return candidates.value.find((c) => c.id === app.candidate_id)
}

function initials(name) {
  if (!name) return '?'
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

function openSchedule(app) {
  scheduleApp.value = app
  scheduleDate.value = ''
  scheduleTime.value = ''
  scheduleError.value = ''
  showSchedule.value = true
}

async function submitSchedule() {
  scheduleError.value = ''
  if (!scheduleDate.value || !scheduleTime.value) {
    scheduleError.value = 'Выберите дату и время'
    return
  }
  scheduleLoading.value = true
  try {
    await api.post('/interviews/', {
      application_id: scheduleApp.value.id,
      scheduled_at: `${scheduleDate.value}T${scheduleTime.value}:00`,
    })
    showSchedule.value = false
    await loadData()
  } catch (e) {
    scheduleError.value = e.response?.data?.detail || 'Ошибка'
  } finally {
    scheduleLoading.value = false
  }
}

async function submitFeedback(interview) {
  const fb = feedbacks.value[interview.id]
  if (!fb?.text?.trim()) return
  try {
    await api.post('/feedbacks/', {
      interview_id: interview.id,
      text: fb.text,
      score_overall: fb.score_overall || null,
      score_technical: fb.score_technical || null,
      score_communication: fb.score_communication || null,
      score_fit: fb.score_fit || null,
      strengths: fb.strengths || null,
      weaknesses: fb.weaknesses || null,
      recommendation: fb.recommendation || null,
    })
    submitted.value[interview.id] = true
    feedbacks.value[interview.id] = { text: '', score_overall: 0, score_technical: 0, score_communication: 0, score_fit: 0, strengths: '', weaknesses: '', recommendation: '' }
    setTimeout(() => { submitted.value[interview.id] = false }, 3000)
  } catch {}
}

function joinCall(roomCode) {
  router.push(`/call/${roomCode}`)
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { dateStyle: 'medium', timeStyle: 'short' })
}

function setScore(interviewId, field, val) {
  if (feedbacks.value[interviewId]) {
    feedbacks.value[interviewId][field] = val
  }
}

const RECOMMENDATIONS = [
  { value: 'recommend', label: 'Рекомендовать', color: 'text-emerald-500 border-emerald-500 bg-emerald-500/10' },
  { value: 'reserve', label: 'Резерв', color: 'text-teal-500 border-teal-500 bg-teal-500/10' },
  { value: 'reject', label: 'Отказать', color: 'text-red-500 border-red-500 bg-red-500/10' },
  { value: 're_interview', label: 'Повторное интервью', color: 'text-orange-500 border-orange-500 bg-orange-500/10' },
]
</script>

<template>
  <div class="p-4 md:p-8 max-w-4xl mx-auto bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <div class="mb-8 md:mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
          <Calendar class="w-7 h-7 text-brand-status-interview" />
          Собеседования
        </h1>
        <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Оценивайте кандидатов и оставляйте профессиональный фидбек</p>
      </div>

      <div class="flex items-center gap-2 px-4 py-2 bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl self-start md:self-auto">
        <div class="w-2 h-2 rounded-full bg-brand-status-interview animate-pulse"></div>
        <span class="text-[10px] md:text-caption text-brand-light-primary dark:text-brand-dark-primary font-bold uppercase tracking-widest">Active session</span>
      </div>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-4 text-brand-light-muted">
      <Loader2 class="w-10 h-10 animate-spin text-brand-status-interview" />
      <p class="text-body font-medium">Синхронизация данных...</p>
    </div>

    <div v-else class="space-y-10">
      <!-- Pending scheduling -->
      <section v-if="pendingApps.length">
        <h2 class="text-heading text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-2 mb-4 px-2">
          <div class="w-1.5 h-6 bg-brand-status-screening rounded-full"></div>
          Ожидают назначения
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            v-for="app in pendingApps"
            :key="app.id"
            class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
          >
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-10 h-10 rounded-xl bg-brand-status-interview/10 flex items-center justify-center shrink-0">
                <span class="text-brand-status-interview text-sm font-bold">{{ initials(candidateForApp(app)?.full_name) }}</span>
              </div>
              <div class="min-w-0">
                <p class="font-bold text-sm text-brand-light-primary dark:text-brand-dark-primary truncate">{{ candidateForApp(app)?.full_name || 'Кандидат' }}</p>
                <p class="text-micro text-brand-light-secondary dark:text-brand-dark-secondary truncate flex items-center gap-1 mt-0.5">
                  <Mail class="w-3 h-3" />
                  {{ candidateForApp(app)?.email }}
                </p>
              </div>
            </div>
            <button
              @click="openSchedule(app)"
              class="w-full sm:w-auto shrink-0 px-4 py-2 bg-brand-status-interview hover:opacity-90 text-white text-micro font-bold rounded-xl transition shadow-lg shadow-brand-status-interview/20 uppercase tracking-tighter"
            >
              Назначить
            </button>
          </div>
        </div>
      </section>

      <!-- Scheduled interviews -->
      <section>
        <h2 class="text-heading text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-2 mb-4 px-2">
          <div class="w-1.5 h-6 bg-brand-status-interview rounded-full"></div>
          Расписание
        </h2>

        <div v-if="!interviews.length" class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-8 md:p-12 text-center">
          <Calendar class="w-8 h-8 text-brand-light-muted mx-auto mb-4" />
          <p class="text-body text-brand-light-secondary dark:text-brand-dark-secondary font-medium">На сегодня встреч не запланировано</p>
        </div>

        <div class="space-y-6">
          <div
            v-for="interview in interviews"
            :key="interview.id"
            class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border shadow-2xl shadow-brand-accent/5 overflow-hidden"
          >
            <!-- Interview header -->
            <div class="p-4 md:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div class="flex items-center gap-4 min-w-0">
                <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center shrink-0">
                  <span class="text-brand-accent text-base font-bold">{{ initials(candidateForInterview(interview)?.full_name) }}</span>
                </div>
                <div class="min-w-0">
                  <h4 class="font-bold text-brand-light-primary dark:text-brand-dark-primary truncate">{{ candidateForInterview(interview)?.full_name || 'Кандидат' }}</h4>
                  <div class="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1">
                    <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary flex items-center gap-1.5 truncate">
                      <Mail class="w-3.5 h-3.5" />
                      {{ candidateForInterview(interview)?.email }}
                    </p>
                    <p class="text-caption text-brand-status-interview font-bold flex items-center gap-1.5">
                      <Calendar class="w-3.5 h-3.5" />
                      {{ formatDate(interview.scheduled_at) }}
                    </p>
                    <span v-if="interview.format" class="text-micro bg-brand-light-elevated dark:bg-brand-dark-elevated px-2 py-0.5 rounded font-medium text-brand-light-secondary dark:text-brand-dark-secondary uppercase">
                      {{ interview.format === 'online' ? '🌐 Онлайн' : interview.format === 'offline' ? '🏢 Офлайн' : '📞 Телефон' }}
                    </span>
                  </div>
                  <p v-if="interview.location" class="text-micro text-brand-light-muted dark:text-brand-dark-muted mt-1">📍 {{ interview.location }}</p>
                </div>
              </div>
              <button
                @click="joinCall(interview.room_code)"
                class="w-full md:w-auto shrink-0 flex items-center justify-center gap-2.5 px-6 py-3 text-sm font-bold rounded-2xl bg-brand-accent hover:bg-brand-accent-hover text-white shadow-lg shadow-brand-accent/20 transition-all"
              >
                <Video class="w-5 h-5" />
                Начать собеседование
              </button>
            </div>

            <!-- Structured feedback form -->
            <div class="p-6 border-t border-brand-light-border dark:border-brand-dark-border space-y-6">
              <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-2">
                <MessageSquare class="w-5 h-5 text-brand-accent" />
                Оценка кандидата
              </h3>

              <!-- Score fields -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div v-for="field in [
                  { key: 'score_overall', label: 'Общая оценка' },
                  { key: 'score_technical', label: 'Проф. знания' },
                  { key: 'score_communication', label: 'Коммуникация' },
                  { key: 'score_fit', label: 'Соответствие должности' },
                ]" :key="field.key" class="space-y-1.5">
                  <label class="text-caption font-bold text-brand-light-secondary dark:text-brand-dark-secondary">{{ field.label }}</label>
                  <div class="flex gap-1">
                    <button
                      v-for="n in 5"
                      :key="n"
                      @click="setScore(interview.id, field.key, n)"
                      :class="[
                        'w-8 h-8 rounded-lg text-sm font-bold transition-all',
                        feedbacks[interview.id]?.[field.key] >= n
                          ? 'bg-brand-accent text-white shadow-sm'
                          : 'bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-muted dark:text-brand-dark-muted hover:bg-brand-accent/20'
                      ]"
                    >
                      {{ n }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Strengths / Weaknesses -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="space-y-2">
                  <label class="text-caption font-bold text-emerald-500 flex items-center gap-1.5">
                    <ThumbsUp class="w-4 h-4" /> Сильные стороны
                  </label>
                  <textarea
                    v-model="feedbacks[interview.id].strengths"
                    rows="3"
                    placeholder="Что понравилось..."
                    class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-sm text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-emerald-500/50 transition-all resize-none"
                  />
                </div>
                <div class="space-y-2">
                  <label class="text-caption font-bold text-red-400 flex items-center gap-1.5">
                    <ThumbsDown class="w-4 h-4" /> Слабые стороны
                  </label>
                  <textarea
                    v-model="feedbacks[interview.id].weaknesses"
                    rows="3"
                    placeholder="Зоны роста..."
                    class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-sm text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-red-500/50 transition-all resize-none"
                  />
                </div>
              </div>

              <!-- Comment -->
              <div class="space-y-2">
                <label class="text-caption font-bold text-brand-light-secondary dark:text-brand-dark-secondary">Комментарий</label>
                <textarea
                  v-model="feedbacks[interview.id].text"
                  rows="3"
                  placeholder="Общие впечатления о кандидате..."
                  class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/5 transition-all resize-none"
                />
              </div>

              <!-- Recommendation -->
              <div class="space-y-2">
                <label class="text-caption font-bold text-brand-light-secondary dark:text-brand-dark-secondary">Рекомендация</label>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="rec in RECOMMENDATIONS"
                    :key="rec.value"
                    @click="feedbacks[interview.id].recommendation = feedbacks[interview.id].recommendation === rec.value ? '' : rec.value"
                    :class="[
                      'px-4 py-2 rounded-xl text-sm font-bold border transition-all',
                      feedbacks[interview.id]?.recommendation === rec.value
                        ? rec.color
                        : 'border-brand-light-border dark:border-brand-dark-border text-brand-light-secondary dark:text-brand-dark-secondary hover:border-brand-accent/30'
                    ]"
                  >
                    {{ rec.label }}
                  </button>
                </div>
              </div>

              <!-- Submit -->
              <div class="flex items-center justify-between">
                <button
                  @click="submitFeedback(interview)"
                  class="px-8 py-3 bg-brand-status-hired hover:opacity-90 text-white text-body font-bold rounded-xl transition shadow-lg shadow-emerald-500/20 disabled:opacity-50"
                  :disabled="!feedbacks[interview.id]?.text?.trim()"
                >
                  Опубликовать отзыв
                </button>
                <div v-if="submitted[interview.id]" class="flex items-center gap-2 text-emerald-500 font-bold animate-in fade-in slide-in-from-right-4">
                  <Check class="w-5 h-5" />
                  ГОТОВО
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Schedule modal -->
    <div
      v-if="showSchedule"
      class="fixed inset-0 bg-brand-dark-base/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="showSchedule = false"
    >
      <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border shadow-2xl p-8 w-full max-w-sm animate-in zoom-in-95 duration-200">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-xl bg-brand-status-interview/10 flex items-center justify-center">
            <Calendar class="w-5 h-5 text-brand-status-interview" />
          </div>
          <div>
            <h2 class="text-heading text-brand-light-primary dark:text-brand-dark-primary leading-tight">Дата встречи</h2>
            <p class="text-micro text-brand-light-secondary dark:text-brand-dark-secondary mt-1 font-bold">{{ scheduleApp && candidateForApp(scheduleApp)?.full_name }}</p>
          </div>
        </div>

        <div class="space-y-5">
          <div class="space-y-2">
            <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Дата</label>
            <input v-model="scheduleDate" type="date" class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-status-interview transition-all" />
          </div>
          <div class="space-y-2">
            <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Время</label>
            <input v-model="scheduleTime" type="time" class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-status-interview transition-all" />
          </div>
          <div v-if="scheduleError" class="flex items-start gap-3 bg-red-500/5 border border-red-500/20 rounded-xl p-4">
            <X class="w-5 h-5 text-red-500 shrink-0" />
            <p class="text-caption text-red-500">{{ scheduleError }}</p>
          </div>
        </div>

        <div class="flex gap-3 mt-8">
          <button @click="showSchedule = false" class="flex-1 py-3 text-body font-bold text-brand-light-secondary dark:text-brand-dark-secondary border border-brand-light-border dark:border-brand-dark-border rounded-xl hover:bg-brand-light-elevated transition-all">Отмена</button>
          <button @click="submitSchedule" :disabled="scheduleLoading" class="flex-2 py-3 bg-brand-status-interview hover:opacity-90 disabled:opacity-60 text-white text-body font-bold rounded-xl transition flex items-center justify-center gap-2">
            <Loader2 v-if="scheduleLoading" class="w-4 h-4 animate-spin" />
            {{ scheduleLoading ? 'Сохранение...' : 'Назначить' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
