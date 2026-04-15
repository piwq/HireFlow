<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useThemeStore } from '@/stores/theme.js'
import api from '@/api/index.js'

const auth = useAuthStore()
const theme = useThemeStore()

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
  <div class="min-h-screen bg-slate-50 dark:bg-[#0D0F1A]">
    <!-- Header -->
    <header class="bg-white dark:bg-[#151827] border-b border-slate-200 dark:border-[#2A2F4A] px-6 py-4 sticky top-0 z-10">
      <div class="max-w-2xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
            <span class="text-white text-xs font-bold">H</span>
          </div>
          <span class="font-bold text-slate-900 dark:text-slate-100 text-base tracking-tight">HireFlow</span>
          <span class="text-slate-300 dark:text-slate-700 mx-1">·</span>
          <span class="text-sm text-slate-500 dark:text-slate-400">Кандидат</span>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="theme.toggle()"
            class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition text-sm"
          >
            {{ theme.dark ? '☀️' : '🌙' }}
          </button>
          <button
            @click="auth.logout(); $router.push('/login')"
            class="px-3 py-1.5 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition"
          >
            Выйти
          </button>
        </div>
      </div>
    </header>

    <div class="max-w-2xl mx-auto p-6 space-y-4">
      <!-- Profile card -->
      <div class="bg-white dark:bg-[#151827] rounded-2xl border border-slate-200 dark:border-[#2A2F4A] shadow-sm p-6 space-y-5">
        <div class="flex items-center gap-3 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div class="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-950/50 flex items-center justify-center">
            <span class="text-indigo-600 dark:text-indigo-400 text-lg">👤</span>
          </div>
          <div>
            <h1 class="text-base font-bold text-slate-900 dark:text-slate-100">Мой профиль</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400">Заполните данные для поиска работы</p>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              ФИО <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.full_name"
              type="text"
              placeholder="Иванов Иван Иванович"
              class="w-full bg-slate-50 dark:bg-[#1E2235] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Навыки</label>
            <textarea
              v-model="form.skills"
              rows="3"
              placeholder="Python, FastAPI, PostgreSQL, Docker..."
              class="w-full bg-slate-50 dark:bg-[#1E2235] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition resize-none"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Опыт работы</label>
            <textarea
              v-model="form.experience"
              rows="4"
              placeholder="2 года в ООО Компания, должность Backend Developer..."
              class="w-full bg-slate-50 dark:bg-[#1E2235] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition resize-none"
            />
          </div>

          <!-- File upload -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Резюме (PDF/Word)</label>
            <input ref="fileInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="uploadResume" />
            <div
              @click="fileInput.click()"
              class="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-indigo-400 dark:hover:border-indigo-600 rounded-xl p-4 cursor-pointer transition-colors group"
            >
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 group-hover:bg-indigo-50 dark:group-hover:bg-indigo-950/40 flex items-center justify-center transition-colors">
                  <span class="text-slate-500 dark:text-slate-400 group-hover:text-indigo-500 text-base">📄</span>
                </div>
                <div>
                  <p class="text-sm font-medium text-slate-700 dark:text-slate-300">
                    {{ uploading ? 'Загружаю...' : form.resume_url ? 'Заменить файл' : 'Загрузить резюме' }}
                  </p>
                  <p class="text-xs text-slate-400 dark:text-slate-500">PDF, DOC, DOCX</p>
                </div>
              </div>
            </div>
            <a
              v-if="form.resume_url"
              :href="form.resume_url"
              target="_blank"
              class="inline-flex items-center gap-1.5 mt-2 text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              <span>🔗</span> Просмотреть загруженное резюме
            </a>
          </div>
        </div>

        <div v-if="error" class="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-lg px-3.5 py-2.5">
          <p class="text-red-600 dark:text-red-400 text-sm">{{ error }}</p>
        </div>
        <div v-if="saved" class="bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/50 rounded-lg px-3.5 py-2.5">
          <p class="text-emerald-600 dark:text-emerald-400 text-sm">✓ Профиль сохранён!</p>
        </div>

        <button
          @click="saveProfile"
          :disabled="saving"
          class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white rounded-lg py-2.5 text-sm font-semibold transition-all shadow-md shadow-indigo-500/25 hover:shadow-lg hover:shadow-indigo-500/30"
        >
          {{ saving ? 'Сохраняю...' : 'Сохранить профиль' }}
        </button>
      </div>

      <!-- Apply to vacancy -->
      <div v-if="vacancies.length" class="bg-white dark:bg-[#151827] rounded-2xl border border-slate-200 dark:border-[#2A2F4A] shadow-sm p-6">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-9 h-9 rounded-lg bg-emerald-100 dark:bg-emerald-950/50 flex items-center justify-center">
            <span class="text-emerald-600 dark:text-emerald-400">💼</span>
          </div>
          <h2 class="text-base font-semibold text-slate-900 dark:text-slate-100">Откликнуться на вакансию</h2>
        </div>
        <div class="flex gap-2">
          <select
            v-model="selectedVacancy"
            class="flex-1 bg-slate-50 dark:bg-[#1E2235] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition"
          >
            <option v-for="v in vacancies" :key="v.id" :value="v.id">{{ v.title }}</option>
          </select>
          <button
            @click="applyToVacancy"
            :disabled="applying"
            class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-60 text-white rounded-lg text-sm font-semibold transition"
          >
            {{ applying ? '...' : 'Откликнуться' }}
          </button>
        </div>
        <p v-if="applied" class="text-emerald-600 dark:text-emerald-400 text-sm mt-2">✓ Отклик отправлен!</p>
      </div>
    </div>
  </div>
</template>
