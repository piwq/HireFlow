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
  GraduationCap,
  Languages,
  Award,
  Camera,
  Save,
  Sparkles,
  Video,
  ChevronRight,
  HelpCircle,
  Smartphone,
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
const photoInput = ref(null)
const uploading = ref(false)
const saving = ref(false)
const saved = ref(false)
const error = ref('')
const formErrors = ref({})
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
const telegramLinkUrl = ref('')
const activeTab = ref('general')
const myInterviews = ref([])
const initiatingTgUpload = ref(false)
const tgUploadType = ref('')
const showUploadModal = ref(false)
const uploadModalConfig = ref({ type: 'other', title: 'Загрузка файла', accept: '*', target: 'document' })
const isDragging = ref(false)

function scrollToTop() {
  const el = document.getElementById('main-content')
  if (el) el.scrollTo({ top: 0, behavior: 'smooth' })
}

// Structured data
const workExperiences = ref([])
const educations = ref([])
const languages = ref([])
const projects = ref([])
const profileId = ref(null)
const uploadingPhoto = ref(false)

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
    profileId.value = data.id
    // Load structured data
    if (data.id) {
      const [weRes, edRes, lnRes, prRes] = await Promise.all([
        api.get('/profile-items/work-experience').catch(() => ({ data: [] })),
        api.get('/profile-items/education').catch(() => ({ data: [] })),
        api.get('/profile-items/languages').catch(() => ({ data: [] })),
        api.get('/profile-items/projects').catch(() => ({ data: [] })),
      ])
      workExperiences.value = weRes.data
      educations.value = edRes.data
      languages.value = lnRes.data
      projects.value = prRes.data
    }
  } catch {}
  try {
    const [vacRes, appsRes, docsRes, tgRes, intRes] = await Promise.all([
      api.get('/vacancies/'),
      api.get('/applications/my'),
      api.get('/documents/my'),
      api.get('/users/telegram-bot-info'),
      api.get('/interviews/my').catch(() => ({ data: [] })),
    ])
    vacancies.value = vacRes.data
    myApps.value = appsRes.data
    documents.value = docsRes.data
    myInterviews.value = intRes.data
    botUsername.value = tgRes.data.bot_username || ''
    telegramLinked.value = tgRes.data.telegram_linked
    const appliedIds = new Set(appsRes.data.map(a => a.vacancy_id))
    const available = vacRes.data.find(v => !appliedIds.has(v.id))
    if (available) selectedVacancy.value = available.id
    else if (vacRes.data.length) selectedVacancy.value = vacRes.data[0].id
  } catch {}
})

async function openTelegramLink() {
  try {
    const { data } = await api.get('/users/telegram-link')
    window.open(data.url, '_blank')
  } catch {}
}

function formatPhone(val) {
  if (!val) return ''
  let cleaned = val.replace(/\D/g, '')
  // Handle leading 7 or 8
  if (cleaned.startsWith('7') || cleaned.startsWith('8')) {
    cleaned = cleaned.substring(1)
  }
  // Limit to 10 digits
  cleaned = cleaned.substring(0, 10)
  
  if (cleaned.length === 0) return ''
  
  let formatted = '+7'
  if (cleaned.length > 0) {
    formatted += ' (' + cleaned.substring(0, 3)
  }
  if (cleaned.length > 2) {
    formatted += ') ' + cleaned.substring(3, 6)
  }
  if (cleaned.length > 5) {
    formatted += '-' + cleaned.substring(6, 8)
  }
  if (cleaned.length > 7) {
    formatted += '-' + cleaned.substring(8, 10)
  }
  return formatted
}

function handlePhoneInput(e) {
  const val = e.target.value
  form.value.phone = formatPhone(val)
}

function handleNumericInput(e, obj, field) {
  obj[field] = e.target.value.replace(/\D/g, '')
}

async function handleGosuslugiUpload() {
  const file = gosuslugiInput.value.files[0]
  if (!file) return
  
  parsingGosuslugi.value = true
  error.value = ''
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const res = await api.post('/candidates/parse-gosuslugi', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    if (res.data.status === 'success') {
      // Просто обновляем весь список с бэкенда — это надежнее и теперь быстро
      const weRes = await api.get('/profile-items/work-experience')
      workExperiences.value = weRes.data
      
      saved.value = true
      setTimeout(() => (saved.value = false), 3000)
    } else if (res.data.error) {
      error.value = res.data.error
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Ошибка при разборе файла Госуслуг'
  } finally {
    parsingGosuslugi.value = false
    gosuslugiInput.value.value = ''
    if (!error.value) showGosuslugiModal.value = false
  }
}

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
    await saveProfile()
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

function validateForm() {
  formErrors.value = {}
  if (!form.value.full_name?.trim()) formErrors.value.full_name = 'ФИО обязательно'
  if (form.value.phone && form.value.phone.length < 18) formErrors.value.phone = 'Введите полный номер телефона'
  
  // Numeric validation for salary
  if (form.value.salary_from && isNaN(Number(form.value.salary_from))) formErrors.value.salary = 'Зарплата должна быть числом'
  if (form.value.salary_to && isNaN(Number(form.value.salary_to))) formErrors.value.salary = 'Зарплата должна быть числом'

  if (form.value.salary_from && form.value.salary_to && Number(form.value.salary_from) > Number(form.value.salary_to)) {
    formErrors.value.salary = 'ЗП "от" не может быть больше "до"'
  }
  
  return Object.keys(formErrors.value).length === 0
}

async function saveProfile() {
  error.value = ''
  if (!validateForm()) { error.value = 'Исправьте ошибки в форме'; return }
  
  // Sanitize data: convert empty strings to null for numeric fields to avoid Pydantic errors
  const payload = { ...form.value }
  if (payload.salary_from === '' || payload.salary_from === undefined) payload.salary_from = null
  if (payload.salary_to === '' || payload.salary_to === undefined) payload.salary_to = null
  
  // Auto-prefix URLs
  const urlFields = ['linkedin', 'github', 'portfolio']
  urlFields.forEach(f => {
    if (payload[f] && payload[f].trim() && !payload[f].startsWith('http')) {
      payload[f] = 'https://' + payload[f].trim()
    }
  })
  
  saving.value = true
  try {
    await api.post('/candidates/profile', payload)
    saved.value = true
    setTimeout(() => (saved.value = false), 2500)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}

async function uploadPhoto() {
  const file = photoInput.value.files[0]
  if (!file) return
  uploadingPhoto.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const { data } = await api.post('/files/upload-resume', fd)
    form.value.photo_url = data.url
    await saveProfile()
  } catch { error.value = 'Ошибка загрузки фото' }
  finally { uploadingPhoto.value = false }
}

async function initTelegramUpload(docType = 'other') {
  if (!telegramLinked.value) {
    error.value = 'Сначала привяжите Telegram в настройках (кнопка вверху)'
    return
  }
  initiatingTgUpload.value = true
  tgUploadType.value = docType
  error.value = ''
  
  try {
    await api.post('/documents/init-tg-upload', { doc_type: docType })
    
    // Start polling for new documents
    const initialCount = documents.value.length
    const profileInitialPhoto = form.value.photo_url
    
    const interval = setInterval(async () => {
      try {
        const { data: docs } = await api.get('/documents/my')
        const { data: profile } = await api.get('/candidates/me')
        
        const fileFound = docs.length > initialCount || profile.photo_url !== profileInitialPhoto
        
        if (fileFound) {
          documents.value = docs
          form.value.photo_url = profile.photo_url
          initiatingTgUpload.value = false
          tgUploadType.value = ''
          clearInterval(interval)
          showUploadModal.value = false
          saved.value = true
          setTimeout(() => { saved.value = false }, 3000)
        }
      } catch {
        clearInterval(interval)
        initiatingTgUpload.value = false
      }
    }, 3000)
    
    // Stop after 3 minutes
    setTimeout(() => {
      clearInterval(interval)
      initiatingTgUpload.value = false
    }, 180000)
    
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка инициализации Telegram загрузки'
    initiatingTgUpload.value = false
  }
}

function openUploadModal(type = 'other', target = 'document') {
  uploadModalConfig.value = {
    type,
    target, // 'document', 'photo', 'resume'
    title: type === 'photo' ? 'Фото профиля' : type === 'resume' ? 'Резюме' : 'Документ',
    accept: type === 'photo' ? 'image/*' : type === 'resume' ? '.pdf,.doc,.docx' : '*',
  }
  showUploadModal.value = true
}

async function handleFileSelect(event) {
  const file = event.target.files[0]
  if (!file) return
  await processUpload(file)
}

async function handleFileDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (!file) return
  await processUpload(file)
}

async function processUpload(file) {
  const { target, type } = uploadModalConfig.value
  
  if (target === 'photo') {
    await performUpload(file, '/files/upload-resume', (url) => { form.value.photo_url = url })
  } else if (target === 'resume') {
    await performUpload(file, '/files/upload-resume', (url) => { form.value.resume_url = url })
  } else {
    await performUploadDocument(file, type)
  }
  
  if (!error.value) {
    showUploadModal.value = false
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  }
}

async function performUpload(file, endpoint, callback) {
  const fd = new FormData()
  fd.append('file', file)
  try {
    saving.value = true
    const { data } = await api.post(endpoint, fd)
    callback(data.url)
    await saveProfile()
  } catch {
    error.value = 'Ошибка загрузки файла'
  } finally {
    saving.value = false
  }
}

async function performUploadDocument(file, type) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('doc_type', type)
  try {
    uploadingDoc.value = true
    const { data } = await api.post('/documents/upload', fd)
    documents.value.push(data)
  } catch {
    error.value = 'Ошибка загрузки документа'
  } finally {
    uploadingDoc.value = false
  }
}

// Structured profile CRUD
async function addWorkExperience() {
  if (!profileId.value) return
  try {
    const res = await api.post('/profile-items/work-experience', { candidate_id: profileId.value, company: 'Новая компания', position: 'Должность' })
    workExperiences.value.push(res.data)
  } catch {}
}
async function updateWorkExperience(we) {
  try {
    await api.put(`/profile-items/work-experience/${we.id}`, we)
  } catch {}
}
async function deleteWorkExperience(id) {
  try {
    await api.delete(`/profile-items/work-experience/${id}`)
    workExperiences.value = workExperiences.value.filter(w => w.id !== id)
  } catch {}
}
async function addEducation() {
  if (!profileId.value) return
  try {
    const res = await api.post('/profile-items/education', { candidate_id: profileId.value, institution: 'Новое учебное заведение' })
    educations.value.push(res.data)
  } catch {}
}
async function updateEducation(ed) {
  try {
    await api.put(`/profile-items/education/${ed.id}`, ed)
  } catch {}
}
async function deleteEducation(id) {
  try {
    await api.delete(`/profile-items/education/${id}`)
    educations.value = educations.value.filter(e => e.id !== id)
  } catch {}
}
async function addLanguage() {
  if (!profileId.value) return
  try {
    const res = await api.post('/profile-items/languages', { candidate_id: profileId.value, name: 'Новый язык' })
    languages.value.push(res.data)
  } catch {}
}
async function updateLanguage(ln) {
  try {
    await api.put(`/profile-items/languages/${ln.id}`, ln)
  } catch {}
}
async function deleteLanguage(id) {
  try {
    await api.delete(`/profile-items/languages/${id}`)
    languages.value = languages.value.filter(l => l.id !== id)
  } catch {}
}
async function addProject() {
  if (!profileId.value) return
  try {
    const res = await api.post('/profile-items/projects', { candidate_id: profileId.value, title: 'Новый проект' })
    projects.value.push(res.data)
  } catch {}
}
async function updateProject(pr) {
  try {
    await api.put(`/profile-items/projects/${pr.id}`, pr)
  } catch {}
}
const gosuslugiInput = ref(null)
const parsingGosuslugi = ref(false)
const showGosuslugiModal = ref(false)

async function deleteProject(id) {
  try {
    await api.delete(`/profile-items/projects/${id}`)
    projects.value = projects.value.filter(p => p.id !== id)
  } catch {}
}
const suggestingField = ref(null)
async function getAIHint(field, item) {
  suggestingField.value = `${field}-${item.id || 'new'}`
  try {
    const context = field === 'responsibilities' ? item.responsibilities : field === 'description' ? item.description : ''
    const { data } = await api.post('/candidates/ai/suggest', { field, context })
    if (field === 'responsibilities') item.responsibilities = data.suggestion
    if (field === 'description') item.description = data.suggestion
  } catch {}
  finally { suggestingField.value = null }
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

function interviewForApp(appId) {
  return myInterviews.value.find(i => i.application_id === appId)
}

const alreadyAppliedIds = computed(() => new Set(myApps.value.map(a => a.vacancy_id)))
const availableVacancies = computed(() => vacancies.value.filter(v => !alreadyAppliedIds.value.has(v.id)))

const completeness = computed(() => {
  const fields = [
    form.value.full_name, form.value.phone, form.value.city,
    form.value.desired_position, form.value.specialization, form.value.level,
    form.value.skills, form.value.experience, form.value.resume_url,
  ]
  let filled = fields.filter(f => f && String(f).trim()).length
  let total = fields.length

  // Add weight for structured data
  if (workExperiences.value.length > 0) filled += 1
  if (educations.value.length > 0) filled += 1
  if (languages.value.length > 0) filled += 1
  if (projects.value.length > 0) filled += 1
  total += 4

  return Math.min(100, Math.round((filled / total) * 100))
})
</script>

<template>
  <div class="h-full flex flex-col bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <div class="flex-1 flex flex-col lg:flex-row overflow-hidden">
      <!-- Sidebar / Navigation -->
      <aside class="w-full lg:w-80 lg:shrink-0 bg-brand-light-surface dark:bg-brand-dark-surface border-b lg:border-b-0 lg:border-r border-brand-light-border dark:border-brand-dark-border flex flex-col overflow-y-auto">
        <!-- Personal Summary Card -->
        <div class="p-6 border-b border-brand-light-border dark:border-brand-dark-border">
          <div class="flex flex-col items-center text-center gap-4">
            <div class="relative group">
              <div class="w-24 h-24 rounded-3xl bg-brand-light-elevated dark:bg-brand-dark-elevated border-2 border-dashed border-brand-light-border dark:border-brand-dark-border flex items-center justify-center overflow-hidden cursor-pointer hover:border-brand-accent transition-all ring-4 ring-brand-accent/5" @click="openUploadModal('photo', 'photo')">
                <img v-if="form.photo_url" :src="form.photo_url" class="w-full h-full object-cover" />
                <Camera v-else class="w-8 h-8 text-brand-light-muted" />
                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                  <Upload class="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
            
            <div class="space-y-1">
              <h2 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">{{ form.full_name || 'Ваш профиль' }}</h2>
              <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary flex items-center justify-center gap-1">
                <MapPin class="w-3 h-3" /> {{ form.city || 'Город не указан' }}
              </p>
            </div>

            <!-- Completeness -->
            <div class="w-full space-y-2 pt-2">
              <div class="flex items-center justify-between text-micro font-bold">
                <span class="text-brand-light-secondary dark:text-brand-dark-secondary">Заполнение</span>
                <span :class="completeness >= 80 ? 'text-emerald-500' : completeness >= 50 ? 'text-yellow-500' : 'text-red-400'">{{ completeness }}%</span>
              </div>
              <div class="h-1.5 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-700"
                  :class="completeness >= 80 ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]' : completeness >= 50 ? 'bg-yellow-400' : 'bg-red-400'"
                  :style="{ width: completeness + '%' }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Nav Menu -->
        <nav class="p-4 space-y-1">
          <button
            v-for="item in [
              { id: 'general', label: 'Основное', icon: User },
              { id: 'career', label: 'Карьера', icon: Briefcase },
              { id: 'education', label: 'Образование', icon: GraduationCap },
              { id: 'skills', label: 'Навыки', icon: Zap },
              { id: 'documents', label: 'Документы', icon: FileText },
              { id: 'applications', label: 'Отклики', icon: Send },
            ]"
            :key="item.id"
            @click="activeTab = item.id; scrollToTop()"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all duration-200 group',
              activeTab === item.id 
                ? 'bg-brand-accent text-white shadow-lg shadow-brand-accent/20' 
                : 'text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated hover:text-brand-light-primary dark:hover:text-brand-dark-primary'
            ]"
          >
            <component :is="item.icon" :class="['w-5 h-5 transition-transform group-hover:scale-110', activeTab === item.id ? 'text-white' : 'text-brand-light-muted dark:text-brand-dark-muted']" />
            {{ item.label }}
          </button>
        </nav>

        <!-- Bottom Links -->
        <div class="mt-auto p-4 space-y-2">
          <!-- Telegram Status -->
          <div :class="['p-4 rounded-2xl border transition-all', telegramLinked ? 'bg-emerald-500/5 border-emerald-500/10' : 'bg-indigo-500/5 border-indigo-500/10']">
            <div class="flex items-center gap-2 mb-1">
              <Send :class="['w-3.5 h-3.5', telegramLinked ? 'text-emerald-500' : 'text-indigo-500']" />
              <p :class="['text-micro font-black uppercase tracking-wider', telegramLinked ? 'text-emerald-500' : 'text-indigo-500']">Telegram</p>
            </div>
            <p v-if="!telegramLinked" class="text-xs text-brand-light-secondary dark:text-brand-dark-secondary leading-snug mb-3">Получайте уведомления о статусах откликов</p>
            <p v-else class="text-xs text-brand-light-secondary dark:text-brand-dark-secondary leading-snug mb-1">Уведомления подключены</p>
            <button 
              v-if="!telegramLinked"
              @click="openTelegramLink" 
              class="w-full py-2 bg-indigo-500 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-indigo-600 transition-colors shadow-lg shadow-indigo-500/20"
            >
              Подключить
            </button>
          </div>

          <!-- Help Link -->
          <button class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated hover:text-brand-light-primary dark:hover:text-brand-dark-primary transition-all">
            <HelpCircle class="w-5 h-5 text-brand-light-muted dark:text-brand-dark-muted" />
            Нужна помощь?
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <main id="main-content" class="flex-1 overflow-y-auto bg-brand-light-base dark:bg-brand-dark-base p-4 md:p-8 lg:p-10">
        <div class="max-w-4xl mx-auto space-y-8">
          
          <!-- Tabbed Content Areas -->
          <div v-if="activeTab === 'general'" class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <!-- AI Banner -->
            <div class="relative overflow-hidden bg-gradient-to-r from-indigo-500 to-emerald-500 rounded-3xl p-6 shadow-xl shadow-indigo-500/20 text-white flex flex-col md:flex-row items-center justify-between gap-6 cursor-pointer hover:scale-[1.01] transition-transform group" @click="router.push('/candidate/resume-builder')">
              <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10" />
              <div class="relative z-10 flex items-center gap-5">
                <div class="w-14 h-14 bg-white/20 backdrop-blur-xl rounded-2xl flex items-center justify-center shrink-0 border border-white/30 group-hover:rotate-12 transition-transform">
                  <Wand2 class="w-7 h-7 text-white" />
                </div>
                <div>
                  <h2 class="text-lg font-bold leading-tight">Соберите крутое резюме с ИИ</h2>
                  <p class="text-white/80 text-sm mt-0.5">Создайте профессиональный PDF за пару минут</p>
                </div>
              </div>
              <button class="bg-white text-indigo-600 px-6 py-2.5 rounded-2xl font-black whitespace-nowrap shadow-xl relative z-10 hover:shadow-2xl transition-all text-sm uppercase tracking-wider">Перейти</button>
            </div>

            <!-- Personal Info Card -->
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-6 shadow-sm">
              <div class="flex items-center gap-4 pb-6 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 flex items-center justify-center shrink-0">
                  <User class="text-brand-accent w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Личная информация</h3>
                  <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Ваши контактные и биографические данные</p>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="md:col-span-2 space-y-2">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary font-bold">ФИО *</label>
                  <input v-model="form.full_name" type="text" placeholder="Иванов Иван Иванович" :class="['w-full input-field', formErrors.full_name ? 'border-red-400 focus:ring-red-400/10' : '']" />
                  <p v-if="formErrors.full_name" class="text-micro text-red-500 font-medium">{{ formErrors.full_name }}</p>
                </div>
                <div class="space-y-2">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary font-bold">Дата рождения</label>
                  <input v-model="form.birth_date" type="date" class="w-full input-field" />
                </div>
                <div class="space-y-2">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary font-bold">Гражданство</label>
                  <input v-model="form.citizenship" type="text" placeholder="Российская Федерация" class="w-full input-field" />
                </div>
                <div class="space-y-2">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary font-bold">Город</label>
                  <input v-model="form.city" type="text" placeholder="Москва" class="w-full input-field" />
                </div>
                <div class="space-y-2">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary font-bold">Телефон</label>
                  <div class="relative group">
                    <input 
                      :value="form.phone" 
                      @input="handlePhoneInput"
                      type="tel" 
                      placeholder="+7 (999) 000-00-00" 
                      :class="['w-full input-field', formErrors.phone ? 'border-red-400 focus:ring-red-400/10' : '']" 
                      style="padding-left: 3.5rem !important"
                    />
                    <Phone class="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-light-muted group-focus-within:text-brand-accent transition-colors" />
                  </div>
                  <p v-if="formErrors.phone" class="text-micro text-red-500 font-medium">{{ formErrors.phone }}</p>
                </div>
              </div>

              <!-- Social Links -->
              <div class="pt-4 space-y-4">
                <p class="text-micro font-black text-brand-light-muted dark:text-brand-dark-muted uppercase tracking-widest">Ссылки и соцсети</p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div class="space-y-2">
                    <div class="flex items-center gap-2 mb-1">
                      <Globe class="w-3.5 h-3.5 text-brand-light-muted" />
                      <label class="text-caption font-bold text-brand-light-primary dark:text-brand-dark-primary">LinkedIn</label>
                    </div>
                    <input v-model="form.linkedin" type="url" placeholder="https://..." :class="['w-full input-field text-xs py-2', formErrors.linkedin ? 'border-red-400' : '']" />
                  </div>
                  <div class="space-y-2">
                    <div class="flex items-center gap-2 mb-1">
                      <Github class="w-3.5 h-3.5 text-brand-light-muted" />
                      <label class="text-caption font-bold text-brand-light-primary dark:text-brand-dark-primary">GitHub</label>
                    </div>
                    <input v-model="form.github" type="url" placeholder="https://..." :class="['w-full input-field text-xs py-2', formErrors.github ? 'border-red-400' : '']" />
                  </div>
                  <div class="space-y-2">
                    <div class="flex items-center gap-2 mb-1">
                      <Link class="w-3.5 h-3.5 text-brand-light-muted" />
                      <label class="text-caption font-bold text-brand-light-primary dark:text-brand-dark-primary">Портфолио</label>
                    </div>
                    <input v-model="form.portfolio" type="url" placeholder="https://..." class="w-full input-field text-xs py-2" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Career Preferences Card -->
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-6 shadow-sm">
              <div class="flex items-center gap-4 pb-6 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 flex items-center justify-center shrink-0">
                  <Briefcase class="text-brand-accent w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Карьерные предпочтения</h3>
                  <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Желаемая позиция, зарплата и условия</p>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary font-bold">Желаемая должность</label>
                  <input v-model="form.desired_position" type="text" placeholder="Backend Developer" class="w-full input-field" />
                </div>
                <div class="space-y-2">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary font-bold">Специализация</label>
                  <input v-model="form.specialization" type="text" placeholder="Python, FastAPI" class="w-full input-field" />
                </div>
              </div>

              <!-- Level Selection -->
              <div class="space-y-3">
                <label class="text-label text-brand-light-primary dark:text-brand-dark-primary font-bold">Ваш уровень</label>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="l in LEVELS" :key="l"
                    @click="form.level = form.level === l ? '' : l"
                    :class="[
                      'px-5 py-2 rounded-2xl text-xs font-black border transition-all duration-300',
                      form.level === l 
                        ? 'bg-brand-accent text-white border-brand-accent shadow-lg shadow-brand-accent/20' 
                        : 'bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary border-brand-light-border dark:border-brand-dark-border hover:border-brand-accent hover:text-brand-accent'
                    ]"
                  >{{ l }}</button>
                </div>
              </div>

              <!-- Salary & Conditions -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-8 pt-2">
                <div class="space-y-4">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary font-bold">Зарплатные ожидания (₽)</label>
                  <div class="flex items-center gap-3">
                    <div class="flex-1 relative">
                      <input 
                        :value="form.salary_from" 
                        @input="handleNumericInput($event, form, 'salary_from')"
                        type="text" 
                        placeholder="От" 
                        class="w-full input-field py-2.5 text-sm" 
                      />
                    </div>
                    <div class="w-4 h-0.5 bg-brand-light-border dark:bg-brand-dark-border" />
                    <div class="flex-1 relative">
                      <input 
                        :value="form.salary_to" 
                        @input="handleNumericInput($event, form, 'salary_to')"
                        type="text" 
                        placeholder="До" 
                        class="w-full input-field py-2.5 text-sm" 
                      />
                    </div>
                  </div>
                </div>

                <div class="space-y-4">
                  <label class="text-label text-brand-light-primary dark:text-brand-dark-primary font-bold">Формат и переезд</label>
                  <div class="flex flex-col gap-4">
                    <div class="flex flex-wrap gap-2">
                      <button
                        v-for="wf in WORK_FORMATS" :key="wf"
                        @click="form.work_format = form.work_format === wf ? '' : wf"
                        :class="[
                          'px-3.5 py-1.5 rounded-xl text-micro font-bold border transition-all',
                          form.work_format === wf 
                           ? 'bg-brand-accent/20 text-brand-accent border-brand-accent' 
                           : 'bg-transparent text-brand-light-secondary border-brand-light-border dark:border-brand-dark-border hover:border-brand-accent/50'
                        ]"
                      >{{ wf }}</button>
                    </div>
                    <label class="flex items-center gap-3 cursor-pointer group">
                      <div 
                        @click="form.relocation_ready = !form.relocation_ready"
                        :class="['w-9 h-5 rounded-full transition-all relative shrink-0', form.relocation_ready ? 'bg-emerald-500' : 'bg-brand-light-border dark:bg-brand-dark-border']"
                      >
                        <div :class="['absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all', form.relocation_ready ? 'left-[18px]' : 'left-0.5']" />
                      </div>
                      <span class="text-caption text-brand-light-primary dark:text-brand-dark-primary group-hover:text-brand-accent transition-colors">Готов к релокации</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Global Save Profile Button -->
            <div v-if="error" class="pt-6 border-t border-brand-light-border dark:border-brand-dark-border">
              <div class="text-caption text-red-500 font-medium px-4 py-2 bg-red-50 dark:bg-red-500/10 rounded-xl border border-red-200 dark:border-red-500/20">
                {{ error }}
              </div>
            </div>
          </div>

          <!-- Career Tab -->
          <div v-if="activeTab === 'career'" class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-8">
              <div class="flex items-center justify-between gap-4 pb-6 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 flex items-center justify-center shrink-0">
                    <Briefcase class="text-brand-accent w-6 h-6" />
                  </div>
                  <div>
                    <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Опыт работы</h3>
                    <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Ваша профессиональная история</p>
                  </div>
                </div>
                <div class="flex gap-2">
                  <input ref="gosuslugiInput" type="file" accept=".pdf" class="hidden" @change="handleGosuslugiUpload" />
                  <button 
                    @click="showGosuslugiModal = true"
                    class="px-5 py-2.5 bg-brand-accent/10 text-brand-accent rounded-xl hover:bg-brand-accent/20 transition-all text-xs font-black uppercase tracking-widest flex items-center gap-2 group"
                  >
                    <Sparkles class="w-4 h-4 group-hover:scale-110 transition-transform" />
                    Умный импорт
                  </button>
                  <button @click="addWorkExperience" class="px-5 py-2.5 bg-brand-accent text-white rounded-xl shadow-lg shadow-brand-accent/20 hover:scale-105 active:scale-95 transition-all text-xs font-black uppercase tracking-widest flex items-center gap-2">
                    <Plus class="w-4 h-4" /> Добавить
                  </button>
                </div>
              </div>

              <div class="space-y-6">
                <div v-for="we in workExperiences" :key="we.id" class="p-6 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-3xl border border-brand-light-border dark:border-brand-dark-border space-y-5 group relative">
                  <button @click="deleteWorkExperience(we.id)" class="absolute top-4 right-4 p-2 text-brand-light-muted hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all">
                    <Trash2 class="w-4 h-4" />
                  </button>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-2">
                      <label class="text-micro font-black text-brand-light-muted uppercase tracking-widest">Компания</label>
                      <input v-model="we.company" @blur="updateWorkExperience(we)" type="text" class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-accent/10 outline-none transition-all" />
                    </div>
                    <div class="space-y-2">
                      <label class="text-micro font-black text-brand-light-muted uppercase tracking-widest">Должность</label>
                      <input v-model="we.position" @blur="updateWorkExperience(we)" type="text" class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-accent/10 outline-none transition-all" />
                    </div>
                    <div class="md:col-span-2 space-y-2">
                      <label class="text-micro font-black text-brand-light-muted uppercase tracking-widest">Период работы</label>
                      <input v-model="we.period" @blur="updateWorkExperience(we)" type="text" placeholder="Май 2020 — Настоящее время" class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-brand-accent/10 outline-none transition-all" />
                    </div>
                  </div>

                  <div class="space-y-3">
                    <div class="flex items-center justify-between">
                      <label class="text-micro font-black text-brand-light-muted uppercase tracking-widest">Обязанности и достижения</label>
                      <button 
                        @click="getAIHint('responsibilities', we)"
                        :disabled="suggestingField === `responsibilities-${we.id}`"
                        class="flex items-center gap-1.5 text-micro font-black text-brand-accent uppercase tracking-widest hover:opacity-80 disabled:opacity-50"
                      >
                        <Loader2 v-if="suggestingField === `responsibilities-${we.id}`" class="w-3 h-3 animate-spin" />
                        <Sparkles v-else class="w-3 h-3" />
                        {{ suggestingField === `responsibilities-${we.id}` ? 'Думаю...' : 'ИИ Улучшение' }}
                      </button>
                    </div>
                    <textarea v-model="we.responsibilities" @blur="updateWorkExperience(we)" rows="4" class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-brand-accent/10 outline-none transition-all resize-none" />
                  </div>
                </div>
                
                <div v-if="workExperiences.length === 0" class="py-12 text-center border-2 border-dashed border-brand-light-border dark:border-brand-dark-border rounded-3xl">
                  <p class="text-sm text-brand-light-muted italic">Добавьте ваш первый опыт работы</p>
                </div>
              </div>
            </div>

            <!-- Projects Section -->
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-8">
              <div class="flex items-center justify-between gap-4 pb-6 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center shrink-0">
                    <Zap class="text-indigo-500 w-6 h-6" />
                  </div>
                  <div>
                    <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Проекты</h3>
                    <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Ваши лучшие кейсы и разработки</p>
                  </div>
                </div>
                <button @click="addProject" class="px-5 py-2.5 bg-indigo-500 text-white rounded-xl shadow-lg shadow-indigo-500/20 hover:scale-105 active:scale-95 transition-all text-xs font-black uppercase tracking-widest flex items-center gap-2">
                  <Plus class="w-4 h-4" /> Добавить
                </button>
              </div>

              <div class="grid grid-cols-1 gap-6">
                <div v-for="pr in projects" :key="pr.id" class="p-6 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-3xl border border-brand-light-border dark:border-brand-dark-border space-y-4 group relative">
                  <button @click="deleteProject(pr.id)" class="absolute top-4 right-4 p-2 text-brand-light-muted hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all">
                    <Trash2 class="w-4 h-4" />
                  </button>
                  <div class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div class="space-y-2">
                        <label class="text-micro font-black text-brand-light-muted uppercase tracking-widest">Название проекта</label>
                        <input v-model="pr.title" @blur="updateProject(pr)" type="text" class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2 text-sm outline-none" />
                      </div>
                      <div class="space-y-2">
                        <label class="text-micro font-black text-brand-light-muted uppercase tracking-widest">Ссылка</label>
                        <input v-model="pr.url" @blur="updateProject(pr)" type="url" placeholder="https://github.com/..." class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2 text-sm outline-none" />
                      </div>
                    </div>
                    <div class="space-y-2">
                      <label class="text-micro font-black text-brand-light-muted uppercase tracking-widest">Описание</label>
                      <textarea v-model="pr.description" @blur="updateProject(pr)" rows="2" class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2 text-sm outline-none resize-none" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Education Tab -->
          <div v-if="activeTab === 'education'" class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-8">
              <div class="flex items-center justify-between gap-4 pb-6 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 flex items-center justify-center shrink-0">
                    <GraduationCap class="text-brand-accent w-6 h-6" />
                  </div>
                  <div>
                    <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Образование</h3>
                    <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Ваши дипломы и курсы</p>
                  </div>
                </div>
                <button @click="addEducation" class="px-5 py-2.5 bg-brand-accent text-white rounded-xl shadow-lg shadow-brand-accent/20 hover:scale-105 active:scale-95 transition-all text-xs font-black uppercase tracking-widest flex items-center gap-2">
                  <Plus class="w-4 h-4" /> Добавить
                </button>
              </div>

              <div class="grid grid-cols-1 gap-6">
                <div v-for="ed in educations" :key="ed.id" class="p-6 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-3xl border border-brand-light-border dark:border-brand-dark-border space-y-4 group relative">
                  <button @click="deleteEducation(ed.id)" class="absolute top-4 right-4 p-2 text-brand-light-muted hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all">
                    <Trash2 class="w-4 h-4" />
                  </button>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                      <label class="text-micro font-black text-brand-light-muted uppercase tracking-widest">Учебное заведение</label>
                      <input v-model="ed.institution" @blur="updateEducation(ed)" type="text" class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2 text-sm outline-none" />
                    </div>
                    <div class="space-y-2">
                      <label class="text-micro font-black text-brand-light-muted uppercase tracking-widest">Специальность</label>
                      <input v-model="ed.specialization" @blur="updateEducation(ed)" type="text" class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2 text-sm outline-none" />
                    </div>
                    <div class="space-y-2">
                      <label class="text-micro font-black text-brand-light-muted uppercase tracking-widest">Год выпуска</label>
                      <input 
                        :value="ed.year" 
                        @input="handleNumericInput($event, ed, 'year')"
                        @blur="updateEducation(ed)" 
                        type="text" 
                        placeholder="2022" 
                        class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2 text-sm outline-none" 
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Languages Section -->
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-8">
              <div class="flex items-center justify-between gap-4 pb-6 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center shrink-0">
                    <Languages class="text-emerald-500 w-6 h-6" />
                  </div>
                  <div>
                    <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Владение языками</h3>
                    <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Иностранные языки и уровни</p>
                  </div>
                </div>
                <button @click="addLanguage" class="px-5 py-2.5 bg-emerald-500 text-white rounded-xl shadow-lg shadow-emerald-500/20 hover:scale-105 active:scale-95 transition-all text-xs font-black uppercase tracking-widest flex items-center gap-2">
                  <Plus class="w-4 h-4" /> Добавить
                </button>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div v-for="l in languages" :key="l.id" class="flex items-center gap-3 p-3 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-2xl border border-brand-light-border dark:border-brand-dark-border group">
                  <input v-model="l.name" @blur="updateLanguage(l)" type="text" placeholder="Язык" class="flex-1 bg-transparent border-none outline-none text-sm font-bold pl-2" />
                  <input v-model="l.level" @blur="updateLanguage(l)" type="text" placeholder="B2" class="w-16 bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-lg px-2 py-1 text-xs text-center outline-none" />
                  <button @click="deleteLanguage(l.id)" class="p-1.5 text-brand-light-muted hover:text-red-500 transition-colors">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Skills Tab -->
          <div v-if="activeTab === 'skills'" class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-8">
              <div class="flex items-center gap-4 pb-6 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 flex items-center justify-center shrink-0">
                  <Zap class="text-brand-accent w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Навыки и экспертиза</h3>
                  <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Ваши ключевые компетенции</p>
                </div>
              </div>

              <div class="space-y-6">
                <div class="space-y-3">
                  <label class="text-xs font-black text-brand-light-muted dark:text-brand-dark-muted uppercase tracking-widest pl-1">Ключевые навыки (через запятую)</label>
                  <textarea v-model="form.skills" rows="3" placeholder="Python, Vue.js, Tailwind, Docker, PostgreSQL..." class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl px-5 py-4 text-sm focus:ring-4 focus:ring-brand-accent/10 transition-all outline-none resize-none" />
                  
                  <!-- Skills Chips Preview -->
                  <div v-if="form.skills?.trim()" class="flex flex-wrap gap-2 pt-2">
                    <span
                      v-for="skill in form.skills.split(',').map(s => s.trim()).filter(Boolean)"
                      :key="skill"
                      class="px-3 py-1.5 bg-brand-accent/5 text-brand-accent border border-brand-accent/10 rounded-xl text-xs font-bold transition-all hover:bg-brand-accent/10"
                    >{{ skill }}</span>
                  </div>
                </div>

                <div class="space-y-3 relative group">
                  <label class="text-xs font-black text-brand-light-muted dark:text-brand-dark-muted uppercase tracking-widest pl-1">Краткое резюме (About Me)</label>
                  <textarea v-model="form.experience" rows="6" placeholder="Расскажите о своем опыте в свободной форме..." class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl px-5 py-4 text-sm focus:ring-4 focus:ring-brand-accent/10 transition-all outline-none resize-none" />
                </div>
              </div>
            </div>
          </div>

          <!-- Documents Tab -->
          <div v-if="activeTab === 'documents'" class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <!-- Resume Section -->
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-6">
              <div class="flex items-center gap-4 pb-6 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 flex items-center justify-center shrink-0">
                  <FileText class="text-brand-accent w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Основное резюме</h3>
                  <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Файл, который увидят HR в первую очередь</p>
                </div>
              </div>

              <input ref="fileInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="uploadResume" />
              <div
                @click="openUploadModal('resume', 'resume')"
                class="border-2 border-dashed border-brand-light-border dark:border-brand-dark-border hover:border-brand-accent dark:hover:border-brand-accent rounded-3xl p-10 cursor-pointer transition-all group text-center space-y-4"
              >
                <div class="w-16 h-16 rounded-2xl bg-brand-light-elevated dark:bg-brand-dark-elevated flex items-center justify-center mx-auto group-hover:scale-110 group-hover:shadow-xl transition-all">
                  <Upload v-if="!uploading" class="w-8 h-8 text-brand-light-muted group-hover:text-brand-accent transition-colors" />
                  <Loader2 v-else class="w-8 h-8 animate-spin text-brand-accent" />
                </div>
                <div>
                  <p class="text-body font-bold text-brand-light-primary dark:text-brand-dark-primary">Выберите файл резюме</p>
                  <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">PDF, DOC или DOCX до 10MB</p>
                </div>
              </div>

              <div v-if="form.resume_url" class="p-4 bg-brand-accent/5 border border-brand-accent/20 rounded-2xl flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <div class="w-10 h-10 rounded-xl bg-brand-accent/10 flex items-center justify-center">
                    <FileText class="w-5 h-5 text-brand-accent" />
                  </div>
                  <span class="text-sm font-bold text-brand-light-primary dark:text-brand-dark-primary">resume.pdf</span>
                </div>
                <div class="flex items-center gap-2">
                  <a :href="form.resume_url" target="_blank" class="px-3 py-1.5 bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-lg text-xs font-bold hover:border-brand-accent transition-all flex items-center gap-2">
                    <ExternalLink class="w-3.5 h-3.5" /> Открыть
                  </a>
                </div>
              </div>
            </div>

            <!-- Other Documents -->
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-6">
              <div class="flex items-center justify-between gap-4 pb-6 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="flex items-center gap-4">
                  <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 flex items-center justify-center shrink-0">
                    <Plus class="text-brand-accent w-6 h-6" />
                  </div>
                  <div>
                    <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Прочие документы</h3>
                    <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Дипломы, сертификаты, портфолио</p>
                  </div>
                </div>
                
                <div class="flex gap-2">
                  <select v-model="selectedDocType" class="bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-3 py-2 text-xs font-bold outline-none">
                    <option v-for="dt in DOC_TYPES" :key="dt.value" :value="dt.value">{{ dt.label }}</option>
                  </select>
                  <button
                    @click="openUploadModal(selectedDocType, 'document')"
                    class="px-5 py-2 text-brand-accent bg-brand-accent/5 hover:bg-brand-accent/10 border border-brand-accent/20 rounded-xl text-xs font-black uppercase tracking-widest transition-all"
                  >
                    Загрузить
                  </button>
                </div>
              </div>

              <div v-if="documents.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  v-for="doc in documents"
                  :key="doc.id"
                  class="flex items-center justify-between p-4 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-2xl border border-transparent hover:border-brand-accent/10 transition-all shadow-sm"
                >
                  <div class="flex items-center gap-4 min-w-0">
                    <div class="w-10 h-10 rounded-xl bg-brand-accent/5 flex items-center justify-center shrink-0">
                      <FileText class="w-5 h-5 text-brand-light-muted" />
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm font-bold text-brand-light-primary dark:text-brand-dark-primary truncate">{{ doc.name }}</p>
                      <p class="text-micro text-brand-light-muted uppercase font-black tracking-widest">{{ docTypeLabel(doc.doc_type) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-1 shrink-0">
                    <a :href="doc.url" target="_blank" class="p-2 hover:bg-brand-accent/10 rounded-lg text-brand-accent transition-colors">
                      <ExternalLink class="w-4 h-4" />
                    </a>
                    <button @click="deleteDocument(doc.id)" class="p-2 hover:bg-red-400/10 rounded-lg text-red-500 transition-colors">
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
              <p v-else class="text-center py-8 text-brand-light-muted text-sm italic">Вы еще не загрузили дополнительные документы</p>
            </div>
          </div>

          <!-- Applications Tab -->
          <div v-if="activeTab === 'applications'" class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <!-- Status Overview -->
            <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border p-6 md:p-8 space-y-8">
              <div class="flex items-center gap-4 pb-6 border-b border-brand-light-border dark:border-brand-dark-border">
                <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 flex items-center justify-center shrink-0">
                  <Zap class="text-brand-accent w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Ваши активности</h3>
                  <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Отклики на вакансии и их статус</p>
                </div>
              </div>

              <!-- Available Vacancies (New Apply) -->
              <div v-if="availableVacancies.length > 0" class="space-y-4">
                <h4 class="text-sm font-black text-brand-light-muted dark:text-brand-dark-muted uppercase tracking-widest pl-1">Доступные вакансии</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-for="v in availableVacancies" :key="v.id" class="p-6 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-3xl border border-transparent hover:border-brand-accent/30 transition-all group">
                     <div class="flex justify-between items-start gap-4 mb-3">
                       <h5 class="text-body font-black text-brand-light-primary dark:text-brand-dark-primary group-hover:text-brand-accent transition-colors">{{ v.title }}</h5>
                       <div class="px-2 py-1 bg-brand-accent/10 text-brand-accent rounded text-[10px] font-black uppercase tracking-tighter">New</div>
                     </div>
                     <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary mb-6 line-clamp-2">{{ v.description }}</p>
                     <button
                        @click="selectedVacancy = v.id; applyToVacancy()"
                        :disabled="applying"
                        class="w-full py-2.5 bg-brand-accent hover:bg-brand-accent-hover text-white rounded-xl text-xs font-black uppercase tracking-widest transition-all shadow-lg shadow-brand-accent/20 hover:-translate-y-0.5"
                      >
                        {{ applying && selectedVacancy === v.id ? 'Отправка...' : 'Откликнуться' }}
                      </button>
                  </div>
                </div>
              </div>

              <!-- My Applications List -->
              <div v-if="myApps.length > 0" class="space-y-4">
                <h4 class="text-sm font-black text-brand-light-muted dark:text-brand-dark-muted uppercase tracking-widest pl-1">Активные отклики</h4>
                <div class="space-y-3">
                  <div
                    v-for="app in myApps"
                    :key="app.id"
                    class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-2xl border border-brand-light-border dark:border-brand-dark-border"
                  >
                    <div class="space-y-1">
                      <p class="text-sm font-black text-brand-light-primary dark:text-brand-dark-primary">{{ vacancyName(app.vacancy_id) }}</p>
                      <p class="text-xs text-brand-light-muted">Дата подачи: {{ new Date(app.created_at).toLocaleDateString() }}</p>
                    </div>
                    <div class="flex items-center gap-3">
                      <span :class="['px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shrink-0 border', STATUS_COLORS[app.status] || 'bg-brand-light-elevated text-brand-light-secondary shadow-sm']">
                        {{ STATUS_LABELS[app.status] || app.status }}
                      </span>
                      <button
                        v-if="['interview', 'manager_interview'].includes(app.status) && interviewForApp(app.id)"
                        @click.stop="router.push(`/call/${interviewForApp(app.id).room_code}`)"
                        class="flex items-center gap-2 px-3 py-1.5 bg-brand-status-interview/10 text-brand-status-interview rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-brand-status-interview/20 transition-all shadow-sm shrink-0"
                      >
                        <Video class="w-3.5 h-3.5" />
                        Войти
                      </button>
                      <div class="w-1 h-8 bg-brand-light-border dark:bg-brand-dark-border rounded-full hidden md:block" />
                      <button @click="activeTab = 'general'" class="p-2 hover:bg-brand-accent/10 rounded-xl transition-all group">
                        <ChevronRight class="w-5 h-5 text-brand-light-muted group-hover:text-brand-accent transition-colors" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-if="availableVacancies.length === 0 && myApps.length === 0" class="py-20 text-center space-y-4">
                <div class="w-20 h-20 rounded-full bg-brand-light-elevated dark:bg-brand-dark-elevated flex items-center justify-center mx-auto opacity-50">
                  <Zap class="w-10 h-10 text-brand-light-muted" />
                </div>
                <p class="text-body text-brand-light-muted italic">Пока нет доступных вакансий или активных откликов</p>
              </div>
            </div>
          </div>

          <!-- Bottom Actions (Floating on mobile) -->
          <div class="fixed bottom-6 left-6 right-6 md:relative md:bottom-0 md:left-0 md:right-0 z-30 pointer-events-none md:pointer-events-auto">
            <div class="max-w-4xl mx-auto flex items-center justify-center md:justify-end gap-4 pointer-events-auto">
               <div v-if="saved" class="hidden md:flex items-center gap-2 text-emerald-500 font-bold text-sm animate-in fade-in slide-in-from-right-4">
                 <Check class="w-5 h-5" /> Профиль обновлен
               </div>
               <button
                  @click="saveProfile"
                  :disabled="saving"
                  class="px-12 py-4 md:py-3 md:rounded-2xl bg-brand-accent hover:bg-brand-accent-hover text-white rounded-3xl text-sm font-black uppercase tracking-widest transition-all shadow-2xl shadow-brand-accent/40 flex items-center gap-3 active:scale-95 disabled:opacity-50"
                >
                  <Loader2 v-if="saving" class="w-5 h-5 animate-spin" />
                  <Save v-else class="w-5 h-5" />
                  {{ saving ? 'Сохранение...' : 'Обновить всё' }}
                </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
    <!-- Gosuslugi Import Modal -->
    <div v-if="showGosuslugiModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-brand-dark-bg/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div class="bg-brand-light-surface dark:bg-brand-dark-surface w-full max-w-md rounded-3xl border border-brand-light-border dark:border-brand-dark-border shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
        <div class="p-8 space-y-6">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 flex items-center justify-center shrink-0">
              <Sparkles class="text-brand-accent w-6 h-6" />
            </div>
            <div>
              <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Умный импорт</h3>
              <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary text-sm">ИИ заполнит ваш опыт работы за секунды</p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="p-4 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-2xl border border-brand-light-border dark:border-brand-dark-border space-y-3">
              <h4 class="text-xs font-black text-brand-light-primary dark:text-brand-dark-primary uppercase tracking-widest">Инструкция:</h4>
              <ul class="space-y-2">
                <li class="flex items-start gap-3 text-sm text-brand-light-secondary dark:text-brand-dark-secondary">
                  <div class="w-5 h-5 rounded-full bg-brand-accent/20 text-brand-accent flex items-center justify-center text-[10px] font-bold mt-0.5 shrink-0">1</div>
                  <span>Запросите на <b>Госуслугах</b> «Выписку из электронной трудовой книжки»</span>
                </li>
                <li class="flex items-start gap-3 text-sm text-brand-light-secondary dark:text-brand-dark-secondary">
                  <div class="w-5 h-5 rounded-full bg-brand-accent/20 text-brand-accent flex items-center justify-center text-[10px] font-bold mt-0.5 shrink-0">2</div>
                  <span>Скачайте полученный <b>PDF-файл</b></span>
                </li>
                <li class="flex items-start gap-3 text-sm text-brand-light-secondary dark:text-brand-dark-secondary">
                  <div class="w-5 h-5 rounded-full bg-brand-accent/20 text-brand-accent flex items-center justify-center text-[10px] font-bold mt-0.5 shrink-0">3</div>
                  <span>Загрузите его сюда — ИИ сделает остальное</span>
                </li>
              </ul>
            </div>
          </div>

          <div v-if="error" class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-500 text-xs text-center">
            {{ error }}
          </div>

          <div class="flex flex-col gap-3">
            <input ref="gosuslugiInput" type="file" accept=".pdf" class="hidden" @change="handleGosuslugiUpload" />
            <button 
              @click="gosuslugiInput.click()"
              :disabled="parsingGosuslugi"
              class="w-full py-4 bg-brand-accent text-white rounded-2xl font-black uppercase tracking-widest text-sm shadow-xl shadow-brand-accent/20 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:scale-100"
            >
              <Loader2 v-if="parsingGosuslugi" class="w-5 h-5 animate-spin" />
              <Upload v-else class="w-5 h-5" />
              {{ parsingGosuslugi ? 'Обработка файла...' : 'Выбрать PDF файл' }}
            </button>
            <button 
              @click="showGosuslugiModal = false"
              :disabled="parsingGosuslugi"
              class="w-full py-3 text-brand-light-secondary dark:text-brand-dark-secondary text-xs font-bold hover:text-brand-light-primary dark:hover:text-brand-dark-primary transition-colors"
            >
              Отмена
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- Upload Modal -->
    <div v-if="showUploadModal" @click.self="showUploadModal = false" class="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-brand-dark-bg/80 backdrop-blur-md animate-in fade-in duration-300">
      <div class="bg-brand-light-surface dark:bg-brand-dark-surface w-full max-w-xl rounded-[2.5rem] border border-brand-light-border dark:border-brand-dark-border shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
        <div class="p-8 md:p-10 space-y-8">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-2xl bg-brand-accent/10 flex items-center justify-center shrink-0">
                <Upload class="text-brand-accent w-6 h-6" />
              </div>
              <div>
                <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">{{ uploadModalConfig.title }}</h3>
                <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary text-sm">Выберите удобный способ загрузки</p>
              </div>
            </div>
            <button @click="showUploadModal = false" class="p-3 text-brand-light-muted hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated rounded-2xl transition-all">
              <Plus class="w-6 h-6 rotate-45" />
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 h-full">
            <!-- Classic Upload -->
            <div class="space-y-4">
              <label class="text-micro font-black text-brand-light-muted dark:text-brand-dark-muted uppercase tracking-widest pl-1">Локальный файл</label>
              <div
                @click="$refs.modalFileInput.click()"
                @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @drop.prevent="handleFileDrop"
                :class="[
                  'min-h-[260px] rounded-[2rem] border-2 border-dashed flex flex-col items-center justify-center gap-4 cursor-pointer transition-all group p-6 text-center',
                  isDragging ? 'border-brand-accent bg-brand-accent/5 scale-[1.02]' : 'border-brand-light-border dark:border-brand-dark-border hover:border-brand-accent/40 bg-brand-light-elevated dark:bg-brand-dark-elevated'
                ]"
              >
                <input ref="modalFileInput" type="file" :accept="uploadModalConfig.accept" class="hidden" @change="handleFileSelect" />
                <div class="w-16 h-16 rounded-2xl bg-brand-light-surface dark:bg-brand-dark-surface flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:shadow-brand-accent/10 transition-all">
                  <Upload class="w-8 h-8 text-brand-light-muted group-hover:text-brand-accent transition-colors" />
                </div>
                <div class="space-y-1">
                  <p class="text-sm font-bold text-brand-light-primary dark:text-brand-dark-primary">Нажмите или перетащите</p>
                  <p class="text-xs text-brand-light-secondary dark:text-brand-dark-secondary">Поддерживается: {{ uploadModalConfig.accept === 'image/*' ? 'Фото' : 'PDF/Word' }}</p>
                </div>
              </div>
            </div>

            <!-- Telegram Upload -->
            <div class="space-y-4">
              <label class="text-micro font-black text-brand-light-muted dark:text-brand-dark-muted uppercase tracking-widest pl-1">Telegram Бот</label>
              <div 
                class="min-h-[260px] rounded-[2rem] bg-brand-accent/5 border border-brand-accent/10 p-6 flex flex-col justify-between relative overflow-hidden group"
              >
                <div class="space-y-4 relative z-10">
                  <div class="w-10 h-10 rounded-xl bg-brand-accent/10 flex items-center justify-center">
                    <Smartphone class="text-brand-accent w-5 h-5" />
                  </div>
                  <div class="space-y-2">
                    <h4 class="text-sm font-bold text-brand-light-primary dark:text-brand-dark-primary">Загрузка через телефон</h4>
                    <p class="text-[11px] leading-relaxed text-brand-light-secondary dark:text-brand-dark-secondary">
                      Мы отправим запрос в ваш Telegram. Сделайте фото или выберите файл в чате с телефона.
                    </p>
                  </div>
                </div>

                <div class="relative z-10 pt-4">
                  <button 
                    @click="initTelegramUpload(uploadModalConfig.type)"
                    :disabled="initiatingTgUpload || !telegramLinked"
                    :class="[
                      'w-full py-3 rounded-2xl font-black uppercase tracking-widest text-[10px] transition-all flex items-center justify-center gap-2',
                      telegramLinked 
                        ? 'bg-brand-accent text-white shadow-lg shadow-brand-accent/20 hover:scale-[1.02] active:scale-[0.98]' 
                        : 'bg-brand-light-border dark:bg-brand-dark-border text-brand-light-muted cursor-not-allowed'
                    ]"
                  >
                    <Loader2 v-if="initiatingTgUpload" class="w-3.5 h-3.5 animate-spin" />
                    <Smartphone v-else class="w-3.5 h-3.5" />
                    {{ initiatingTgUpload ? 'Ждем...' : telegramLinked ? 'Запросить в TG' : 'Не привязан' }}
                  </button>
                  <p v-if="!telegramLinked" class="text-[9px] text-center mt-2 text-brand-light-muted italic">Нужна привязка</p>
                </div>

                <!-- Abstract background shapes -->
                <div class="absolute -top-12 -right-12 w-32 h-32 bg-brand-accent/5 rounded-full blur-3xl group-hover:bg-brand-accent/10 transition-all" />
              </div>
            </div>
          </div>

          <div v-if="error" class="p-4 bg-red-500/5 border border-red-500/10 rounded-2xl text-red-500 text-xs font-bold text-center animate-in slide-in-from-top-2">
            {{ error }}
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
