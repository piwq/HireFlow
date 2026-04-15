<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import api from '@/api/index.js'

const auth = useAuthStore()

const form = ref({ full_name: '', skills: '', experience: '', resume_url: '' })
const fileInput = ref(null)
const uploading = ref(false)
const saving = ref(false)
const saved = ref(false)
const error = ref('')
const vacancies = ref([])
const applying = ref(false)
const applied = ref(false)
const selectedVacancy = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/candidates/me')
    form.value = { ...data }
  } catch {
    // profile not created yet
  }
  try {
    const { data } = await api.get('/vacancies/')
    vacancies.value = data
    if (data.length) selectedVacancy.value = data[0].id
  } catch {}
})

async function uploadResume() {
  const file = fileInput.value.files[0]
  if (!file) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await api.post('/files/upload-resume', fd)
    form.value.resume_url = data.url
  } catch (e) {
    error.value = 'Ошибка загрузки файла'
  } finally {
    uploading.value = false
  }
}

async function saveProfile() {
  error.value = ''
  if (!form.value.full_name) {
    error.value = 'ФИО обязательно'
    return
  }
  saving.value = true
  try {
    await api.post('/candidates/profile', form.value)
    saved.value = true
    setTimeout(() => (saved.value = false), 2500)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}

async function applyToVacancy() {
  if (!selectedVacancy.value) return
  applying.value = true
  try {
    await api.post('/applications/', { vacancy_id: selectedVacancy.value })
    applied.value = true
    setTimeout(() => (applied.value = false), 3000)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка отклика'
  } finally {
    applying.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-gray-800">Мой профиль</h1>
        <button @click="auth.logout(); $router.push('/login')" class="text-sm text-gray-500 hover:text-red-500">
          Выйти
        </button>
      </div>

      <div class="bg-white rounded-2xl shadow-md p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ФИО *</label>
          <input v-model="form.full_name" type="text" placeholder="Иванов Иван Иванович"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Навыки</label>
          <textarea v-model="form.skills" rows="3" placeholder="Python, FastAPI, PostgreSQL..."
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Опыт работы</label>
          <textarea v-model="form.experience" rows="4" placeholder="2 года в ООО Компания, должность..."
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
        </div>

        <!-- File upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Резюме (PDF/Word)</label>
          <div class="flex gap-2 items-center">
            <input ref="fileInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="uploadResume" />
            <button type="button" @click="fileInput.click()"
              class="px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg text-sm hover:bg-gray-200 transition"
              :disabled="uploading">
              {{ uploading ? 'Загружаю...' : 'Загрузить файл' }}
            </button>
            <a v-if="form.resume_url" :href="form.resume_url" target="_blank"
              class="text-sm text-blue-600 hover:underline truncate max-w-xs">
              Просмотреть резюме
            </a>
          </div>
        </div>

        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
        <p v-if="saved" class="text-green-500 text-sm">Профиль сохранён!</p>

        <button @click="saveProfile" :disabled="saving"
          class="w-full bg-blue-600 text-white rounded-lg py-2 font-medium hover:bg-blue-700 disabled:opacity-50 transition">
          {{ saving ? 'Сохраняю...' : 'Сохранить профиль' }}
        </button>
      </div>

      <!-- Apply to vacancy -->
      <div v-if="vacancies.length" class="bg-white rounded-2xl shadow-md p-6 mt-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-3">Откликнуться на вакансию</h2>
        <div class="flex gap-2">
          <select v-model="selectedVacancy"
            class="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option v-for="v in vacancies" :key="v.id" :value="v.id">{{ v.title }}</option>
          </select>
          <button @click="applyToVacancy" :disabled="applying"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition text-sm">
            {{ applying ? '...' : 'Откликнуться' }}
          </button>
        </div>
        <p v-if="applied" class="text-green-500 text-sm mt-2">Отклик отправлен!</p>
      </div>
    </div>
  </div>
</template>
