<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/index.js'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
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
  Wand2,
  Phone,
  MapPin,
  Globe,
  Github,
  Link,
  DollarSign,
  Trash2,
  Plus,
  Send,
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()
const form = ref({
  full_name: '', skills: '', experience: '', resume_url: '',
  phone: '', city: '', citizenship: '', birth_date: '',
  linkedin: '', github: '', portfolio: '',
  desired_position: '', specialization: '', level: '',
  salary_from: null, salary_to: null,
  employment_type: '', work_format: '', relocation_ready: false,
})
const fileInput = ref(null)
const docFileInput = ref(null)
const uploading = ref(false)
const saving = ref(false)
const saved = ref(false)
const error = ref('')
const vacancies = ref([])
const myApps = ref([])
const applying = ref(false)
const applied = ref(false)
const selectedVacancy = ref('')
const documents = ref([])
const uploadingDoc = ref(false)
const selectedDocType = ref('other')
const botUsername = ref('')
const telegramLinked = ref(false)

const DOC_TYPES = [
  { value: 'resume', label: 'Резюме' },
  { value: 'cover_letter', label: 'Сопроводительное письмо' },
  { value: 'certificate', label: 'Сертификат' },
  { value: 'diploma', label: 'Диплом' },
  { value: 'other', label: 'Иное' },
]

const LEVELS = ['Junior', 'Middle', 'Senior', 'Lead', 'Principal']
const EMPLOYMENT_TYPES = ['Полная занятость', 'Частичная занятость', 'Проектная работа', 'Стажировка']
const WORK_FORMATS = ['Офис', 'Удалённо', 'Гибридный']

onMounted(async () => {
  try {
    const { data } = await api.get('/candidates/me')
    Object.assign(form.value, data)
  } catch {}
  try {
    const [vacRes, appsRes, docsRes, tgRes] = await Promise.all([
      api.get('/vacancies/'),
      api.get('/applications/my'),
      api.get('/documents/my'),
      api.get('/users/telegram-bot-info'),
    ])
    vacancies.value = vacRes.data
    myApps.value = appsRes.data
    documents.value = docsRes.data
    botUsername.value = tgRes.data.bot_username || ''
    telegramLinked.value = tgRes.data.telegram_linked
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

async function uploadDocument() {
  const file = docFileInput.value.files[0]
  if (!file) return
  uploadingDoc.value = true
  error.value = ''
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('doc_type', selectedDocType.value)
    const { data } = await api.post('/documents/upload', fd)
    documents.value.unshift(data)
  } catch {
    error.value = 'Ошибка загрузки документа'
  } finally {
    uploadingDoc.value = false
    docFileInput.value.value = ''
  }
}

async function deleteDocument(docId) {
  try {
    await api.delete(`/documents/${docId}`)
    documents.value = documents.value.filter(d => d.id !== docId)
  } catch {}
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

function docTypeLabel(v) {
  return DOC_TYPES.find(d => d.value === v)?.label || v
}

const selectedVacancyObj = computed(() =>
  vacancies.value.find(v => v.id === selectedVacancy.value)
)

const STATUS_LABELS = {
  new: 'Новый', screening: 'На рассмотрении', interview: 'HR-интервью',
  manager_interview: 'С руководителем', interview_done: 'Проведено',
  awaiting_decision: 'Ожидает решения', reserve: 'Резерв', offer: 'Оффер',
  hired: 'Принят', rejected: 'Отказ', accepted: 'Принят',
}
const STATUS_COLORS = {
  new: 'bg-blue-400/10 text-blue-400', screening: 'bg-yellow-400/10 text-yellow-500',
  interview: 'bg-purple-400/10 text-purple-400', manager_interview: 'bg-indigo-400/10 text-indigo-400',
  interview_done: 'bg-cyan-400/10 text-cyan-500', awaiting_decision: 'bg-orange-400/10 text-orange-400',
  reserve: 'bg-teal-400/10 text-teal-500', offer: 'bg-emerald-400/10 text-emerald-500',
  hired: 'bg-green-500/10 text-green-500', rejected: 'bg-red-400/10 text-red-400',
  accepted: 'bg-green-600/10 text-green-600',
}

function vacancyName(vacancyId) {
  return vacancies.value.find(v => v.id === vacancyId)?.title || `Вакансия #${vacancyId}`
}

const alreadyAppliedIds = computed(() => new Set(myApps.value.map(a => a.vacancy_id)))
const availableVacancies = computed(() => vacancies.value.filter(v => !alreadyAppliedIds.value.has(v.id)))

const completeness = computed(() => {
  const fields = [
    form.value.full_name, form.value.phone, form.value.city,
    form.value.desired_position, form.value.specialization, form.value.level,
    form.value.skills, form.value.experience, form.value.resume_url,
  ]
  const filled = fields.filter(f => f && String(f).trim()).length
  return Math.round((filled / fields.length) * 100)
})
</script>

<template>
  <div class="h-full flex flex-col bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <!-- Header -->
    <div class="p-4 md:p-8 pb-4">
      <div class="flex items-start justify-between gap-4 max-w-5xl">
        <div>
          <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
            <User class="w-7 h-7 text-brand-accent" />
            Профиль
          </h1>
          <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Управляйте вашими данными и находите лучшие предложения</p>
        </div>
        <!-- Completeness badge -->
        <div class="shrink-0 flex flex-col items-end gap-1.5">
          <span class="text-xs font-bold text-brand-light-secondary dark:text-brand-dark-secondary">Профиль заполнен</span>
          <div class="flex items-center gap-2">
            <div class="w-32 h-2 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="completeness >= 80 ? 'bg-emerald-500' : completeness >= 50 ? 'bg-yellow-400' : 'bg-red-400'"
                :style="{ width: completeness + '%' }"
              />
            </div>
            <span class="text-xs font-black" :class="completeness >= 80 ? 'text-emerald-500' : completeness >= 50 ? 'text-yellow-500' : 'text-red-400'">{{ completeness }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="flex-1 p-4 md:p-8 pt-0 overflow-y-auto">
      <!-- AI banner -->
      <div class="max-w-5xl mb-6 relative overflow-hidden bg-gradient-to-r from-indigo-500 to-emerald-500 rounded-2xl p-5 shadow-lg shadow-indigo-500/20 text-white flex flex-col md:flex-row items-center justify-between gap-4 cursor-pointer hover:scale-[1.005] transition-transform" @click="router.push('/candidate/resume-builder')">
        <div class="relative z-10 flex items-center gap-4">
          <div class="w-10 h-10 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center shrink-0">
            <Wand2 class="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 class="text-base font-bold">Соберите крутое резюме за пару минут</h2>
            <p class="text-white/80 text-xs mt-0.5">ИИ-ассистент задаст вопросы и сформирует идеальный PDF-шаблон</p>
          </div>
        </div>
        <button class="bg-white text-indigo-600 px-5 py-2 rounded-xl font-bold whitespace-nowrap shadow-md relative z-10 hover:bg-gray-50 transition-colors text-sm">Перейти в ИИ Конструктор</button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-5xl">
        <!-- Main form -->
        <div class="lg:col-span-2 space-y-5">

          <!-- Personal info -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6 space-y-5">
            <div class="flex items-center gap-3 pb-4 border-b border-brand-light-border dark:border-brand-dark-border">
              <div class="w-9 h-9 rounded-xl bg-brand-accent/10 flex items-center justify-center">
                <User class="text-brand-accent w-4.5 h-4.5" />
              </div>
              <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Личная информация</h3>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="sm:col-span-2 space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">ФИО *</label>
                <input v-model="form.full_name" type="text" placeholder="Иванов Иван Иванович" class="w-full input-field" />
              </div>
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Дата рождения</label>
                <input v-model="form.birth_date" type="date" class="w-full input-field" />
              </div>
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Гражданство</label>
                <input v-model="form.citizenship" type="text" placeholder="Российская Федерация" class="w-full input-field" />
              </div>
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Город</label>
                <input v-model="form.city" type="text" placeholder="Москва" class="w-full input-field" />
              </div>
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Телефон</label>
                <input v-model="form.phone" type="tel" placeholder="+7 999 000-00-00" class="w-full input-field" />
              </div>
            </div>

            <!-- Links row -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">LinkedIn</label>
                <input v-model="form.linkedin" type="url" placeholder="linkedin.com/in/..." class="w-full input-field" />
              </div>
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">GitHub</label>
                <input v-model="form.github" type="url" placeholder="github.com/..." class="w-full input-field" />
              </div>
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Портфолио</label>
                <input v-model="form.portfolio" type="url" placeholder="mysite.ru" class="w-full input-field" />
              </div>
            </div>
          </div>

          <!-- Professional info -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6 space-y-5">
            <div class="flex items-center gap-3 pb-4 border-b border-brand-light-border dark:border-brand-dark-border">
              <div class="w-9 h-9 rounded-xl bg-brand-accent/10 flex items-center justify-center">
                <Briefcase class="text-brand-accent w-4.5 h-4.5" />
              </div>
              <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Карьерные предпочтения</h3>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Желаемая должность</label>
                <input v-model="form.desired_position" type="text" placeholder="Backend Developer" class="w-full input-field" />
              </div>
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Специализация</label>
                <input v-model="form.specialization" type="text" placeholder="Python, FastAPI" class="w-full input-field" />
              </div>
            </div>

            <!-- Level -->
            <div class="space-y-1.5">
              <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Уровень</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="l in LEVELS" :key="l"
                  @click="form.level = form.level === l ? '' : l"
                  :class="['px-3.5 py-1.5 rounded-xl text-sm font-bold border transition-all', form.level === l ? 'bg-brand-accent text-white border-brand-accent' : 'bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary border-brand-light-border dark:border-brand-dark-border hover:border-brand-accent/50']"
                >{{ l }}</button>
              </div>
            </div>

            <!-- Salary -->
            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Зарплата от (₽)</label>
                <input v-model.number="form.salary_from" type="number" placeholder="100 000" class="w-full input-field" />
              </div>
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Зарплата до (₽)</label>
                <input v-model.number="form.salary_to" type="number" placeholder="200 000" class="w-full input-field" />
              </div>
            </div>

            <!-- Employment + Format in 2 cols -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Тип занятости</label>
                <div class="flex flex-wrap gap-1.5">
                  <button
                    v-for="et in EMPLOYMENT_TYPES" :key="et"
                    @click="form.employment_type = form.employment_type === et ? '' : et"
                    :class="['px-3 py-1.5 rounded-lg text-xs font-bold border transition-all', form.employment_type === et ? 'bg-brand-accent text-white border-brand-accent' : 'bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary border-brand-light-border dark:border-brand-dark-border hover:border-brand-accent/50']"
                  >{{ et }}</button>
                </div>
              </div>
              <div class="space-y-1.5">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Формат работы</label>
                <div class="flex flex-wrap gap-1.5">
                  <button
                    v-for="wf in WORK_FORMATS" :key="wf"
                    @click="form.work_format = form.work_format === wf ? '' : wf"
                    :class="['px-3 py-1.5 rounded-lg text-xs font-bold border transition-all', form.work_format === wf ? 'bg-brand-accent text-white border-brand-accent' : 'bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary border-brand-light-border dark:border-brand-dark-border hover:border-brand-accent/50']"
                  >{{ wf }}</button>
                </div>
              </div>
            </div>

            <!-- Relocation -->
            <div class="flex items-center gap-3">
              <button
                @click="form.relocation_ready = !form.relocation_ready"
                :class="['w-10 h-5.5 rounded-full transition-all relative shrink-0', form.relocation_ready ? 'bg-brand-accent' : 'bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border']"
              >
                <div :class="['absolute top-0.5 w-4.5 h-4.5 rounded-full bg-white shadow transition-all', form.relocation_ready ? 'left-[22px]' : 'left-0.5']" />
              </button>
              <span class="text-body text-brand-light-primary dark:text-brand-dark-primary">Готов к переезду / командировкам</span>
            </div>
          </div>

          <!-- Skills & Experience -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6 space-y-4">
            <div class="flex items-center gap-3 pb-4 border-b border-brand-light-border dark:border-brand-dark-border">
              <div class="w-9 h-9 rounded-xl bg-brand-accent/10 flex items-center justify-center">
                <FileText class="text-brand-accent w-4.5 h-4.5" />
              </div>
              <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Навыки и опыт</h3>
            </div>

            <div class="space-y-1.5">
              <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Ключевые навыки</label>
              <textarea v-model="form.skills" rows="2" placeholder="Python, Vue.js, Tailwind, Docker..." class="w-full input-field resize-none" />
              <!-- Skills preview -->
              <div v-if="form.skills?.trim()" class="flex flex-wrap gap-1.5 pt-1">
                <span
                  v-for="skill in form.skills.split(',').map(s => s.trim()).filter(Boolean)"
                  :key="skill"
                  class="text-micro bg-brand-accent/10 text-brand-accent border border-brand-accent/20 px-2 py-0.5 rounded-md font-medium"
                >{{ skill }}</span>
              </div>
            </div>
            <div class="space-y-1.5">
              <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Опыт работы</label>
              <textarea v-model="form.experience" rows="5" placeholder="Расскажите о последних проектах и достижениях..." class="w-full input-field resize-none" />
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
            class="w-full bg-brand-accent hover:bg-brand-accent-hover disabled:opacity-60 text-white rounded-xl py-3.5 text-body font-bold transition-all shadow-lg shadow-brand-accent/25 flex items-center justify-center gap-2"
          >
            <Loader2 v-if="saving" class="w-5 h-5 animate-spin" />
            {{ saving ? 'Сохранение...' : 'Обновить профиль' }}
          </button>
        </div>

        <!-- Sidebar -->
        <div class="space-y-5">

          <!-- ═══ APPLY BLOCK — TOP PRIORITY ═══ -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border-2 border-brand-accent/30 p-5 space-y-4">
            <div class="flex items-center gap-2">
              <div class="w-8 h-8 rounded-lg bg-brand-accent/10 flex items-center justify-center">
                <Zap class="w-4 h-4 text-brand-accent" />
              </div>
              <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Откликнуться</h3>
            </div>

            <!-- No vacancies at all -->
            <div v-if="vacancies.length === 0" class="flex flex-col items-center justify-center py-3 text-center gap-2">
              <Briefcase class="w-8 h-8 text-brand-light-muted dark:text-brand-dark-muted" />
              <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Вакансий пока нет</p>
            </div>

            <!-- Has available vacancies -->
            <div v-else-if="availableVacancies.length > 0" class="space-y-3">
              <div class="relative">
                <select v-model="selectedVacancy" class="w-full input-field appearance-none pr-10 text-sm">
                  <option v-for="v in availableVacancies" :key="v.id" :value="v.id">{{ v.title }}</option>
                </select>
                <ChevronDown class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-light-muted pointer-events-none" />
              </div>
              <p v-if="selectedVacancyObj?.description" class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-xl px-3 py-2 line-clamp-3">
                {{ selectedVacancyObj.description }}
              </p>
              <button
                @click="applyToVacancy"
                :disabled="applying"
                class="w-full bg-brand-accent hover:bg-brand-accent-hover disabled:opacity-60 text-white rounded-xl py-3 text-sm font-bold transition-all shadow-lg shadow-brand-accent/25 flex items-center justify-center gap-2"
              >
                <Loader2 v-if="applying" class="w-4 h-4 animate-spin" />
                {{ applying ? 'Отправка...' : 'Отправить отклик' }}
              </button>
              <p v-if="applied" class="text-caption text-emerald-500 text-center font-medium animate-in fade-in duration-300">✓ Отклик отправлен!</p>
            </div>

            <!-- All applied -->
            <div v-else class="text-center py-2">
              <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Вы откликнулись на все вакансии</p>
            </div>

            <!-- Applied list -->
            <div v-if="myApps.length > 0" class="pt-1 border-t border-brand-light-border dark:border-brand-dark-border space-y-2">
              <p class="text-micro font-bold text-brand-light-muted dark:text-brand-dark-muted uppercase tracking-wider">Мои отклики ({{ myApps.length }})</p>
              <div
                v-for="app in myApps"
                :key="app.id"
                class="flex items-center justify-between gap-2 py-1.5"
              >
                <p class="text-caption text-brand-light-primary dark:text-brand-dark-primary font-medium truncate">{{ vacancyName(app.vacancy_id) }}</p>
                <span :class="['text-micro px-2 py-0.5 rounded-full font-bold shrink-0', STATUS_COLORS[app.status] || 'bg-brand-light-elevated text-brand-light-secondary']">
                  {{ STATUS_LABELS[app.status] || app.status }}
                </span>
              </div>
            </div>
          </div>

          <!-- Telegram notifications -->
          <div v-if="botUsername" class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5 space-y-3">
            <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-2">
              <Send class="w-4.5 h-4.5 text-brand-accent" />
              Telegram
            </h3>
            <div v-if="telegramLinked" class="flex items-center gap-2 text-emerald-500 text-sm font-medium">
              <Check class="w-4 h-4" />
              Уведомления подключены
            </div>
            <template v-else>
              <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Получайте уведомления о статусах заявок и интервью прямо в Telegram</p>
              <a
                :href="`https://t.me/${botUsername}?start=${auth.userId}`"
                target="_blank"
                class="flex items-center justify-center gap-2 w-full py-2.5 bg-[#229ED9] hover:bg-[#1b8bbf] text-white text-sm font-bold rounded-xl transition-colors"
              >
                <Send class="w-4 h-4" />
                Подключить Telegram
              </a>
            </template>
          </div>

          <!-- Resume Upload -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5 space-y-3">
            <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-2">
              <FileText class="w-4.5 h-4.5 text-brand-accent" />
              Резюме
            </h3>
            <input ref="fileInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="uploadResume" />
            <div
              @click="fileInput.click()"
              class="border-2 border-dashed border-brand-light-border dark:border-brand-dark-border hover:border-brand-accent dark:hover:border-brand-accent rounded-xl p-4 cursor-pointer transition-all group flex items-center gap-3"
            >
              <div class="w-9 h-9 rounded-lg bg-brand-light-elevated dark:bg-brand-dark-elevated flex items-center justify-center group-hover:shadow-md transition-all shrink-0">
                <Upload v-if="!uploading" class="w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted group-hover:text-brand-accent transition-colors" />
                <Loader2 v-else class="w-4.5 h-4.5 animate-spin text-brand-accent" />
              </div>
              <div>
                <p class="text-sm font-semibold text-brand-light-primary dark:text-brand-dark-primary">{{ uploading ? 'Загрузка...' : 'Загрузите файл' }}</p>
                <p class="text-micro text-brand-light-muted dark:text-brand-dark-muted">PDF или Word до 10MB</p>
              </div>
            </div>
            <div v-if="form.resume_url" class="p-2.5 bg-brand-accent/5 border border-brand-accent/20 rounded-xl flex items-center justify-between">
              <div class="flex items-center gap-2 overflow-hidden">
                <FileText class="w-4 h-4 text-brand-accent shrink-0" />
                <span class="text-caption text-brand-accent font-medium truncate">resume.pdf</span>
              </div>
              <a :href="form.resume_url" target="_blank" class="p-1.5 hover:bg-brand-accent/10 rounded-lg text-brand-accent transition-colors">
                <ExternalLink class="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          <!-- Documents -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5 space-y-3">
            <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-2">
              <Plus class="w-4.5 h-4.5 text-brand-accent" />
              Документы
            </h3>

            <div class="flex gap-2">
              <div class="relative flex-1">
                <select v-model="selectedDocType" class="w-full input-field appearance-none pr-7 text-sm py-2.5">
                  <option v-for="dt in DOC_TYPES" :key="dt.value" :value="dt.value">{{ dt.label }}</option>
                </select>
                <ChevronDown class="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-brand-light-muted pointer-events-none" />
              </div>
              <input ref="docFileInput" type="file" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" class="hidden" @change="uploadDocument" />
              <button
                @click="docFileInput.click()"
                :disabled="uploadingDoc"
                class="flex items-center justify-center gap-1.5 px-3 py-2.5 bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl text-sm font-bold text-brand-light-secondary dark:text-brand-dark-secondary hover:border-brand-accent/50 hover:text-brand-accent transition-all disabled:opacity-60 shrink-0"
              >
                <Loader2 v-if="uploadingDoc" class="w-4 h-4 animate-spin" />
                <Upload v-else class="w-4 h-4" />
              </button>
            </div>

            <div v-if="documents.length" class="space-y-1.5">
              <div
                v-for="doc in documents"
                :key="doc.id"
                class="flex items-center justify-between p-2 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-xl border border-brand-light-border dark:border-brand-dark-border"
              >
                <div class="flex items-center gap-2 overflow-hidden min-w-0">
                  <FileText class="w-3.5 h-3.5 text-brand-accent shrink-0" />
                  <div class="min-w-0">
                    <p class="text-micro font-medium text-brand-light-primary dark:text-brand-dark-primary truncate">{{ doc.name }}</p>
                    <p class="text-micro text-brand-light-muted dark:text-brand-dark-muted">{{ docTypeLabel(doc.doc_type) }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-1 shrink-0">
                  <a :href="doc.url" target="_blank" class="p-1 hover:bg-brand-accent/10 rounded text-brand-accent transition-colors">
                    <ExternalLink class="w-3 h-3" />
                  </a>
                  <button @click="deleteDocument(doc.id)" class="p-1 hover:bg-red-500/10 rounded text-red-400 transition-colors">
                    <Trash2 class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
            <p v-else class="text-micro text-brand-light-muted dark:text-brand-dark-muted text-center py-1">Документы не загружены</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.input-field {
  @apply bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/10 transition-all;
}
</style>
