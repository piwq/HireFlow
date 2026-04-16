<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'
import {
  User,
  FileText,
  Loader2,
  Check,
  Upload,
  ExternalLink,
  Zap,
  ChevronDown,
  Briefcase,
} from 'lucide-vue-next'

const form = ref({ full_name: '', skills: '', experience: '', resume_url: '' })
const fileInput = ref(null)
const uploading = ref(false)
const saving = ref(false)
const saved = ref(false)
const error = ref('')
const vacancies = ref([])
const myApps = ref([])
const applying = ref(false)
const applied = ref(false)
const selectedVacancy = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/candidates/me')
    form.value = { ...data }
  } catch {}
  try {
    const [vacRes, appsRes] = await Promise.all([
      api.get('/vacancies/'),
      api.get('/applications/my'),
    ])
    vacancies.value = vacRes.data
    myApps.value = appsRes.data
    const appliedIds = new Set(appsRes.data.map(a => a.vacancy_id))
    const available = vacRes.data.find(v => !appliedIds.has(v.id))
    if (available) selectedVacancy.value = available.id
    else if (vacRes.data.length) selectedVacancy.value = vacRes.data[0].id
  } catch {}
})

async function uploadResume() {
  const file = fileInput.value.files[0]
  if (!file) return
  uploading.value = true
  error.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await api.post('/files/upload-resume', fd)
    form.value.resume_url = data.url
  } catch {
    error.value = 'Ошибка загрузки файла'
  } finally {
    uploading.value = false
  }
}

async function saveProfile() {
  error.value = ''
  if (!form.value.full_name) { error.value = 'ФИО обязательно'; return }
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
  error.value = ''
  try {
    const { data } = await api.post('/applications/', { vacancy_id: selectedVacancy.value })
    myApps.value.unshift(data)
    applied.value = true
    setTimeout(() => (applied.value = false), 3000)
    const appliedIds = new Set(myApps.value.map(a => a.vacancy_id))
    const next = vacancies.value.find(v => !appliedIds.has(v.id))
    selectedVacancy.value = next ? next.id : vacancies.value[0]?.id
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка отклика'
  } finally {
    applying.value = false
  }
}
</script>

<template>
  <div class="h-full flex flex-col bg-brand-light-base dark:bg-brand-dark-base antialiased">
      <div class="p-4 md:p-8 pb-4">
        <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
          <User class="w-7 h-7 text-brand-accent" />
          Профиль
        </h1>
        <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Управляйте вашими данными и находите лучшие предложения</p>
      </div>

      <div class="flex-1 p-4 md:p-8 pt-0 overflow-y-auto">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-5xl">
          <!-- Main form -->
          <div class="lg:col-span-2 space-y-6">
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-6">
              <div class="flex items-center gap-3 pb-5 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="w-10 h-10 rounded-xl bg-brand-accent/10 flex items-center justify-center">
                  <User class="text-brand-accent w-5 h-5" />
                </div>
                <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Личная информация</h3>
              </div>

              <div class="space-y-5">
                <div class="space-y-2">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">ФИО</label>
                  <input
                    v-model="form.full_name"
                    type="text"
                    placeholder="Иванов Иван Иванович"
                    class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/10 transition-all"
                  />
                </div>

                <div class="space-y-2">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Ключевые навыки</label>
                  <textarea
                    v-model="form.skills"
                    rows="3"
                    placeholder="Python, Vue.js, Tailwind, Docker..."
                    class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/10 transition-all resize-none"
                  />
                </div>

                <div class="space-y-2">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Опыт работы</label>
                  <textarea
                    v-model="form.experience"
                    rows="5"
                    placeholder="Расскажите о последних проектах и достижениях..."
                    class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/10 transition-all resize-none"
                  />
                </div>
              </div>

              <div v-if="error" class="flex items-start gap-3 bg-red-500/5 border border-red-500/20 rounded-xl p-4">
                <p class="text-caption text-red-500">{{ error }}</p>
              </div>
              <div v-if="saved" class="flex items-center gap-3 bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4">
                <Check class="w-5 h-5 text-emerald-500" />
                <p class="text-caption text-emerald-500">Изменения успешно сохранены!</p>
              </div>

              <button
                @click="saveProfile"
                :disabled="saving"
                class="w-full bg-brand-accent hover:bg-brand-accent-hover disabled:opacity-60 text-white rounded-xl py-3.5 text-body font-bold transition-all shadow-lg shadow-brand-accent/25 flex items-center justify-center gap-2 active:scale-[0.98]"
              >
                <Loader2 v-if="saving" class="w-5 h-5 animate-spin" />
                {{ saving ? 'Сохранение...' : 'Обновить профиль' }}
              </button>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="space-y-6">
            <!-- Resume Upload -->
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6 space-y-4">
              <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-2">
                <FileText class="w-5 h-5 text-brand-accent" />
                Резюме
              </h3>
              <input ref="fileInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="uploadResume" />
              <div
                @click="fileInput.click()"
                class="border-2 border-dashed border-brand-light-border dark:border-brand-dark-border hover:border-brand-accent dark:hover:border-brand-accent rounded-2xl p-6 cursor-pointer transition-all duration-200 group flex flex-col items-center text-center space-y-3 bg-brand-light-elevated/50 dark:bg-brand-dark-elevated/30"
              >
                <div class="w-12 h-12 rounded-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border flex items-center justify-center group-hover:shadow-md transition-all">
                  <Upload v-if="!uploading" class="w-6 h-6 text-brand-light-muted dark:text-brand-dark-muted group-hover:text-brand-accent transition-colors" />
                  <Loader2 v-else class="w-6 h-6 animate-spin text-brand-accent" />
                </div>
                <div>
                  <p class="text-body font-semibold text-brand-light-primary dark:text-brand-dark-primary">
                    {{ uploading ? 'Загрузка...' : 'Загрузите файл' }}
                  </p>
                  <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">PDF или Word до 10MB</p>
                </div>
              </div>
              <div v-if="form.resume_url" class="p-3 bg-brand-accent/5 border border-brand-accent/20 rounded-xl flex items-center justify-between">
                <div class="flex items-center gap-2 overflow-hidden">
                  <FileText class="w-4 h-4 text-brand-accent shrink-0" />
                  <span class="text-caption text-brand-accent font-medium truncate">resume.pdf</span>
                </div>
                <a :href="form.resume_url" target="_blank" class="p-1.5 hover:bg-brand-accent/10 rounded-lg text-brand-accent transition-colors">
                  <ExternalLink class="w-4 h-4" />
                </a>
              </div>
            </div>

            <!-- Apply to vacancy -->
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6 space-y-4">
              <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-2">
                <Zap class="w-5 h-5 text-brand-status-new" />
                Откликнуться
              </h3>
              <div v-if="vacancies.length === 0" class="flex flex-col items-center justify-center py-4 text-center gap-2">
                <Briefcase class="w-8 h-8 text-brand-light-muted dark:text-brand-dark-muted" />
                <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Вакансий пока нет</p>
              </div>
              <div v-else class="space-y-3">
                <div class="relative">
                  <select
                    v-model="selectedVacancy"
                    class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-4 pr-10 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent transition-all appearance-none cursor-pointer"
                  >
                    <option v-for="v in vacancies" :key="v.id" :value="v.id">{{ v.title }}</option>
                  </select>
                  <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-brand-light-muted">
                    <ChevronDown class="w-4 h-4" />
                  </div>
                </div>
                <button
                  @click="applyToVacancy"
                  :disabled="applying"
                  class="w-full bg-brand-status-hired hover:bg-emerald-600 disabled:opacity-60 text-white rounded-xl py-3 text-body font-bold transition-all shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
                >
                  <Loader2 v-if="applying" class="w-4 h-4 animate-spin" />
                  {{ applying ? 'Отправка...' : 'Отправить отклик' }}
                </button>
                <div v-if="applied" class="animate-in fade-in slide-in-from-top-2 duration-300">
                  <p class="text-caption text-emerald-500 text-center font-medium">✓ Отклик успешно отправлен!</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>
