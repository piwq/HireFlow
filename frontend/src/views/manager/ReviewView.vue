<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
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
  ExternalLink,
} from 'lucide-vue-next'

const router = useRouter()

const interviews = ref([])
const candidates = ref([])
const applications = ref([])
const feedbackText = ref({})
const submitted = ref({})
const loading = ref(false)

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
    interviews.value = ivRes.data
    applications.value = appsRes.data
    candidates.value = candidatesRes.data
  } finally {
    loading.value = false
  }
}

const pendingApps = computed(() => {
  const scheduledAppIds = new Set(interviews.value.map((i) => i.application_id))
  return applications.value.filter(
    (a) => a.status === 'interview' && !scheduledAppIds.has(a.id)
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
  const text = feedbackText.value[interview.id]
  if (!text?.trim()) return
  try {
    await api.post('/feedbacks/', { interview_id: interview.id, text })
    submitted.value[interview.id] = true
    feedbackText.value[interview.id] = ''
    setTimeout(() => { submitted.value[interview.id] = false }, 3000)
  } catch {}
}

function joinCall(roomCode) {
  router.push(`/call/${roomCode}`)
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { dateStyle: 'medium', timeStyle: 'short' })
}
</script>

<template>
  <div class="p-4 md:p-8 max-w-4xl mx-auto bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <!-- Page header -->
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
            class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm hover:shadow-md transition-shadow"
          >
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-10 h-10 rounded-xl bg-brand-status-interview/10 flex items-center justify-center shrink-0">
                <span class="text-brand-status-interview text-sm font-bold">
                  {{ initials(candidateForApp(app)?.full_name) }}
                </span>
              </div>
              <div class="min-w-0">
                <p class="font-bold text-sm text-brand-light-primary dark:text-brand-dark-primary truncate">
                  {{ candidateForApp(app)?.full_name || 'Кандидат' }}
                </p>
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
          <div class="w-16 h-16 bg-brand-light-base dark:bg-brand-dark-base rounded-2xl flex items-center justify-center mx-auto mb-4 border border-brand-light-border dark:border-brand-dark-border">
            <Calendar class="w-8 h-8 text-brand-light-muted" />
          </div>
          <p class="text-body text-brand-light-secondary dark:text-brand-dark-secondary font-medium">На сегодня встреч не запланировано</p>
          <p class="text-micro text-brand-light-muted mt-1">Как только HR назначит время, оно появится здесь</p>
        </div>

        <div class="space-y-6">
          <div
            v-for="interview in interviews"
            :key="interview.id"
            class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border shadow-2xl shadow-brand-accent/5 overflow-hidden group hover:border-brand-status-interview/50 transition-colors"
          >
            <!-- Interview header -->
            <div class="p-4 md:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div class="flex items-center gap-4 min-w-0">
                <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center shrink-0">
                  <span class="text-brand-accent text-base font-bold">
                    {{ initials(candidateForInterview(interview)?.full_name) }}
                  </span>
                </div>
                <div class="min-w-0">
                  <div class="flex items-center gap-2">
                    <h4 class="font-bold text-brand-light-primary dark:text-brand-dark-primary truncate">
                      {{ candidateForInterview(interview)?.full_name || 'Кандидат' }}
                    </h4>
                    <span class="text-[10px] bg-brand-status-interview/10 text-brand-status-interview px-2 py-0.5 rounded font-bold uppercase tracking-tighter">Live</span>
                  </div>
                  <div class="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1">
                    <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary flex items-center gap-1.5 truncate">
                      <Mail class="w-3.5 h-3.5" />
                      {{ candidateForInterview(interview)?.email }}
                    </p>
                    <p class="text-caption text-brand-status-interview font-bold flex items-center gap-1.5">
                      <Calendar class="w-3.5 h-3.5" />
                      {{ formatDate(interview.scheduled_at) }}
                    </p>
                  </div>
                </div>
              </div>
              <button
                @click="joinCall(interview.room_code)"
                class="w-full md:w-auto shrink-0 flex items-center justify-center gap-2.5 px-6 py-3 text-sm md:text-body font-bold rounded-2xl transition-all shadow-lg bg-brand-accent hover:bg-brand-accent-hover text-white shadow-brand-accent/20 active:scale-[0.98]"
              >
                <Video class="w-5 h-5" />
                Начать собеседование
              </button>
            </div>

            <!-- Skills -->
            <div
              v-if="candidateForInterview(interview)?.skills"
              class="px-6 py-4 bg-brand-light-elevated/50 dark:bg-brand-dark-elevated/20 border-b border-brand-light-border dark:border-brand-dark-border"
            >
              <div class="flex items-center gap-2">
                <FileText class="w-4 h-4 text-brand-light-muted" />
                <span class="text-caption font-bold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-widest">Core Skills:</span>
                <div class="flex flex-wrap gap-1.5 ml-2">
                  <span v-for="skill in candidateForInterview(interview)?.skills.split(',')" :key="skill" class="text-micro bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border px-2 py-0.5 rounded text-brand-light-primary dark:text-brand-dark-primary">
                    {{ skill.trim() }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Feedback -->
            <div class="p-6 space-y-4">
              <label class="flex items-center gap-2 text-heading text-brand-light-primary dark:text-brand-dark-primary">
                <MessageSquare class="w-5 h-5 text-brand-accent" />
                Заметки и оценка
              </label>
              <textarea
                v-model="feedbackText[interview.id]"
                rows="4"
                placeholder="Опишите сильные стороны кандидата и ваши рекомендации..."
                class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-2xl px-5 py-4 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/5 transition-all resize-none"
              />
              <div class="flex items-center justify-between">
                <button
                  @click="submitFeedback(interview)"
                  class="px-8 py-3 bg-brand-status-hired hover:opacity-90 text-white text-body font-bold rounded-xl transition shadow-lg shadow-emerald-500/20 active:scale-[0.98] disabled:opacity-50"
                  :disabled="!feedbackText[interview.id]?.trim()"
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

    <!-- Schedule modal - Styled properly -->
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
            <input
              v-model="scheduleDate"
              type="date"
              class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-status-interview transition-all"
            />
          </div>
          <div class="space-y-2">
            <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Время</label>
            <input
              v-model="scheduleTime"
              type="time"
              class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-status-interview transition-all"
            />
          </div>
          <div v-if="scheduleError" class="flex items-start gap-3 bg-red-500/5 border border-red-500/20 rounded-xl p-4">
            <X class="w-5 h-5 text-red-500 shrink-0" />
            <p class="text-caption text-red-500">{{ scheduleError }}</p>
          </div>
        </div>
        
        <div class="flex gap-3 mt-8">
          <button
            @click="showSchedule = false"
            class="flex-1 py-3 text-body font-bold text-brand-light-secondary dark:text-brand-dark-secondary border border-brand-light-border dark:border-brand-dark-border rounded-xl hover:bg-brand-light-elevated transition-all"
          >
            Отмена
          </button>
          <button
            @click="submitSchedule"
            :disabled="scheduleLoading"
            class="flex-2 py-3 bg-brand-status-interview hover:opacity-90 disabled:opacity-60 text-white text-body font-bold rounded-xl transition shadow-lg shadow-brand-status-interview/25 flex items-center justify-center gap-2"
          >
            <Loader2 v-if="scheduleLoading" class="w-4 h-4 animate-spin" />
            {{ scheduleLoading ? 'Сохранение...' : 'Назначить' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #2a2f4a;
  border-radius: 10px;
}
</style>
