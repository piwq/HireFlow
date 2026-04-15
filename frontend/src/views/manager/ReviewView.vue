<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api/index.js'
import AppLayout from '@/components/AppLayout.vue'

const interviews = ref([])
const candidates = ref([])
const applications = ref([])
const feedbackText = ref({})
const submitted = ref({})
const jitsiOpen = ref({})
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
  } catch {}
}

function toggleJitsi(id) {
  jitsiOpen.value[id] = !jitsiOpen.value[id]
}

function formatDate(dt) {
  return new Date(dt).toLocaleString('ru-RU', { dateStyle: 'medium', timeStyle: 'short' })
}
</script>

<template>
  <AppLayout>
    <div class="p-6 max-w-3xl">
      <!-- Page header -->
      <div class="mb-6">
        <h1 class="text-xl font-bold text-slate-900 dark:text-slate-100">Собеседования</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Управляйте собеседованиями и оставляйте отзывы</p>
      </div>

      <div v-if="loading" class="flex items-center gap-2 text-slate-400 py-6">
        <span class="animate-spin">⟳</span> Загружаю...
      </div>

      <!-- Pending scheduling -->
      <div v-if="pendingApps.length" class="mb-6">
        <h2 class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
          Ожидают назначения
        </h2>
        <div class="space-y-2">
          <div
            v-for="app in pendingApps"
            :key="app.id"
            class="bg-white dark:bg-[#151827] rounded-xl border border-slate-200 dark:border-[#2A2F4A] p-4 flex items-center justify-between gap-4"
          >
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-9 h-9 rounded-lg bg-violet-100 dark:bg-violet-950/50 flex items-center justify-center shrink-0">
                <span class="text-violet-600 dark:text-violet-400 text-xs font-bold">
                  {{ initials(candidateForApp(app)?.full_name) }}
                </span>
              </div>
              <div class="min-w-0">
                <p class="font-semibold text-sm text-slate-800 dark:text-slate-200 truncate">
                  {{ candidateForApp(app)?.full_name || 'Кандидат' }}
                </p>
                <p class="text-xs text-slate-400 dark:text-slate-500 truncate">
                  {{ candidateForApp(app)?.email }}
                </p>
              </div>
            </div>
            <button
              @click="openSchedule(app)"
              class="shrink-0 px-3.5 py-2 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium rounded-lg transition shadow-sm shadow-violet-500/20"
            >
              Назначить
            </button>
          </div>
        </div>
      </div>

      <!-- Scheduled interviews -->
      <div>
        <h2 class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
          Запланированные собеседования
        </h2>

        <div v-if="!interviews.length && !loading" class="bg-white dark:bg-[#151827] rounded-xl border border-slate-200 dark:border-[#2A2F4A] p-8 text-center">
          <p class="text-slate-400 dark:text-slate-500 text-sm">Нет запланированных собеседований</p>
        </div>

        <div class="space-y-4">
          <div
            v-for="interview in interviews"
            :key="interview.id"
            class="bg-white dark:bg-[#151827] rounded-2xl border border-slate-200 dark:border-[#2A2F4A] shadow-sm overflow-hidden"
          >
            <!-- Interview header -->
            <div class="p-5 flex items-start justify-between gap-4">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-950/50 flex items-center justify-center shrink-0">
                  <span class="text-indigo-600 dark:text-indigo-400 text-sm font-bold">
                    {{ initials(candidateForInterview(interview)?.full_name) }}
                  </span>
                </div>
                <div class="min-w-0">
                  <p class="font-semibold text-slate-800 dark:text-slate-200">
                    {{ candidateForInterview(interview)?.full_name || 'Кандидат' }}
                  </p>
                  <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
                    {{ candidateForInterview(interview)?.email }}
                  </p>
                  <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
                    📅 {{ formatDate(interview.scheduled_at) }}
                  </p>
                </div>
              </div>
              <button
                @click="toggleJitsi(interview.id)"
                :class="[
                  'shrink-0 flex items-center gap-2 px-3.5 py-2 text-sm font-medium rounded-lg transition shadow-sm',
                  jitsiOpen[interview.id]
                    ? 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
                    : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/20'
                ]"
              >
                <span>📹</span>
                {{ jitsiOpen[interview.id] ? 'Закрыть' : 'Войти в звонок' }}
              </button>
            </div>

            <!-- Jitsi iframe -->
            <div v-if="jitsiOpen[interview.id]" class="border-t border-slate-100 dark:border-slate-800">
              <iframe
                :src="`https://meet.jit.si/hr-platform-${interview.room_code}`"
                allow="camera; microphone; fullscreen; display-capture"
                class="w-full h-72"
                frameborder="0"
              />
            </div>

            <!-- Skills -->
            <div
              v-if="candidateForInterview(interview)?.skills"
              class="px-5 py-3 bg-slate-50 dark:bg-[#1E2235]/50 border-t border-slate-100 dark:border-slate-800"
            >
              <p class="text-xs text-slate-500 dark:text-slate-400">
                <span class="font-medium text-slate-600 dark:text-slate-300">Навыки:</span>
                {{ candidateForInterview(interview)?.skills }}
              </p>
            </div>

            <!-- Feedback -->
            <div class="px-5 py-4 border-t border-slate-100 dark:border-slate-800 space-y-3">
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">
                Отзыв о кандидате
              </label>
              <textarea
                v-model="feedbackText[interview.id]"
                rows="3"
                placeholder="Опишите впечатление от собеседования..."
                class="w-full bg-slate-50 dark:bg-[#1E2235] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition resize-none"
              />
              <div class="flex items-center gap-3">
                <button
                  @click="submitFeedback(interview)"
                  class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition shadow-sm shadow-emerald-500/20"
                >
                  Сохранить отзыв
                </button>
                <span v-if="submitted[interview.id]" class="text-emerald-500 text-sm">✓ Отзыв сохранён!</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Schedule modal -->
    <div
      v-if="showSchedule"
      class="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50 p-4"
      @click.self="showSchedule = false"
    >
      <div class="bg-white dark:bg-[#1E2235] rounded-2xl border border-slate-200 dark:border-[#2A2F4A] shadow-2xl p-6 w-full max-w-sm">
        <h2 class="text-lg font-bold text-slate-900 dark:text-slate-100 mb-1">Назначить собеседование</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mb-5">
          {{ scheduleApp && candidateForApp(scheduleApp)?.full_name }}
        </p>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Дата</label>
            <input
              v-model="scheduleDate"
              type="date"
              class="w-full bg-slate-50 dark:bg-[#151827] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Время</label>
            <input
              v-model="scheduleTime"
              type="time"
              class="w-full bg-slate-50 dark:bg-[#151827] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition"
            />
          </div>
          <div v-if="scheduleError" class="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-lg px-3.5 py-2.5">
            <p class="text-red-600 dark:text-red-400 text-sm">{{ scheduleError }}</p>
          </div>
        </div>
        <div class="flex gap-2 mt-5">
          <button
            @click="showSchedule = false"
            class="flex-1 py-2.5 border border-slate-300 dark:border-slate-700 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition"
          >
            Отмена
          </button>
          <button
            @click="submitSchedule"
            :disabled="scheduleLoading"
            class="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-60 text-white text-sm font-semibold rounded-lg transition shadow-md shadow-violet-500/25"
          >
            {{ scheduleLoading ? 'Создаю...' : 'Назначить' }}
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
