<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import api from '@/api/index.js'

const auth = useAuthStore()

const interviews = ref([])
const candidates = ref([])
const applications = ref([])
const feedbackText = ref({})
const submitted = ref({})
const jitsiOpen = ref({})
const loading = ref(false)

// initiate interview modal
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

// Applications in "interview" status that don't have an interview yet
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
  <div class="min-h-screen bg-gray-50">
    <div class="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
      <h1 class="text-xl font-bold text-gray-800">Руководитель — Собеседования</h1>
      <button @click="auth.logout(); $router.push('/login')" class="text-sm text-gray-500 hover:text-red-500">
        Выйти
      </button>
    </div>

    <div class="max-w-3xl mx-auto p-6 space-y-6">
      <p v-if="loading" class="text-gray-500">Загружаю...</p>

      <!-- Pending: candidates ready for interview but not yet scheduled -->
      <div v-if="pendingApps.length">
        <h2 class="text-base font-semibold text-gray-700 mb-3">Ожидают назначения собеседования</h2>
        <div class="space-y-2">
          <div v-for="app in pendingApps" :key="app.id"
            class="bg-white rounded-xl shadow-sm p-4 flex justify-between items-center">
            <div>
              <p class="font-medium text-gray-800">{{ candidateForApp(app)?.full_name || 'Кандидат' }}</p>
              <p class="text-sm text-gray-500">{{ candidateForApp(app)?.email }}</p>
            </div>
            <button @click="openSchedule(app)"
              class="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition">
              Назначить
            </button>
          </div>
        </div>
      </div>

      <!-- Scheduled interviews -->
      <div>
        <h2 class="text-base font-semibold text-gray-700 mb-3">Запланированные собеседования</h2>
        <p v-if="!interviews.length" class="text-gray-400 text-center py-6">Нет запланированных собеседований</p>

        <div v-for="interview in interviews" :key="interview.id"
          class="bg-white rounded-2xl shadow-sm p-5 space-y-3 mb-4">
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold text-gray-800">
                {{ candidateForInterview(interview)?.full_name || 'Кандидат' }}
              </p>
              <p class="text-sm text-gray-500">{{ candidateForInterview(interview)?.email }}</p>
              <p class="text-sm text-gray-400 mt-0.5">{{ formatDate(interview.scheduled_at) }}</p>
            </div>
            <button @click="toggleJitsi(interview.id)"
              class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition">
              {{ jitsiOpen[interview.id] ? 'Закрыть звонок' : '📹 Войти в звонок' }}
            </button>
          </div>

          <div v-if="jitsiOpen[interview.id]" class="rounded-xl overflow-hidden border border-gray-200">
            <iframe
              :src="`https://meet.jit.si/hr-platform-${interview.room_code}`"
              allow="camera; microphone; fullscreen; display-capture"
              class="w-full h-64"
              frameborder="0"
            />
          </div>

          <div v-if="candidateForInterview(interview)?.skills"
            class="text-sm text-gray-600 bg-gray-50 rounded-lg px-3 py-2">
            <span class="font-medium">Навыки:</span> {{ candidateForInterview(interview)?.skills }}
          </div>

          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">Отзыв о кандидате</label>
            <textarea v-model="feedbackText[interview.id]" rows="3"
              placeholder="Опишите впечатление от собеседования..."
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
            <div class="flex items-center gap-3">
              <button @click="submitFeedback(interview)"
                class="px-4 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition">
                Сохранить отзыв
              </button>
              <span v-if="submitted[interview.id]" class="text-green-500 text-sm">Отзыв сохранён!</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Schedule modal -->
    <div v-if="showSchedule" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
      @click.self="showSchedule = false">
      <div class="bg-white rounded-2xl shadow-xl p-6 w-full max-w-sm">
        <h2 class="text-lg font-bold text-gray-800 mb-4">Назначить собеседование</h2>
        <p class="text-sm text-gray-600 mb-4">{{ scheduleApp && candidateForApp(scheduleApp)?.full_name }}</p>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Дата</label>
            <input v-model="scheduleDate" type="date"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Время</label>
            <input v-model="scheduleTime" type="time"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500" />
          </div>
          <p v-if="scheduleError" class="text-red-500 text-sm">{{ scheduleError }}</p>
        </div>
        <div class="flex gap-2 mt-5">
          <button @click="showSchedule = false"
            class="flex-1 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition text-sm">
            Отмена
          </button>
          <button @click="submitSchedule" :disabled="scheduleLoading"
            class="flex-1 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition text-sm">
            {{ scheduleLoading ? 'Создаю...' : 'Назначить' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
