<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/index.js'
import InterviewModal from './InterviewModal.vue'
import {
  ArrowLeft, User, FileText, ExternalLink, Calendar, MessageSquare,
  Clock, CheckCircle, XCircle, Loader2, Star, Mail, Phone,
  MapPin, Globe, Github, Briefcase, DollarSign, Link, StickyNote, Plus, Trash2,
  Edit2,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const candidateId = computed(() => Number(route.params.id))

const candidate = ref(null)
const applications = ref([])
const documents = ref([])
const interviews = ref([])
const feedbacks = ref([])
const statusHistory = ref([])
const notes = ref([])
const newNote = ref('')
const loading = ref(true)

const STATUS_LABELS = {
  new: 'Новый', screening: 'На рассмотрении', interview: 'Назначено HR-интервью',
  manager_interview: 'Интервью с руководителем', interview_done: 'Интервью проведено',
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
const REC_LABELS = {
  recommend: 'Рекомендовать', reserve: 'Резерв', reject: 'Отказать', re_interview: 'Повторное интервью',
}
const REC_COLORS = {
  recommend: 'text-emerald-500', reserve: 'text-teal-500', reject: 'text-red-400', re_interview: 'text-orange-400',
}
const DOC_LABELS = {
  resume: 'Резюме', cover_letter: 'Сопр. письмо', certificate: 'Сертификат', diploma: 'Диплом', other: 'Иное',
}
const FORMAT_LABELS = { online: 'Онлайн', offline: 'Офлайн', phone: 'Телефон' }

const selectedInterview = ref(null)
const selectedApplication = ref(null)
const showInterviewModal = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const [allCandidates, allApps, allInterviews, allFeedbacks, allDocs] = await Promise.all([
      api.get('/candidates/'),
      api.get('/applications/'),
      api.get('/interviews/'),
      api.get('/feedbacks/'),
      api.get(`/documents/candidate/${candidateId.value}`),
    ])

    candidate.value = allCandidates.data.find(c => c.id === candidateId.value)
    if (!candidate.value) { router.push('/hr'); return }

    // Filter applications for this candidate
    applications.value = allApps.data.filter(a => a.candidate_id === candidateId.value)

    // Get interviews for these applications
    const appIds = new Set(applications.value.map(a => a.id))
    interviews.value = allInterviews.data.filter(i => appIds.has(i.application_id))

    // Get feedbacks for these interviews
    const ivIds = new Set(interviews.value.map(i => i.id))
    feedbacks.value = allFeedbacks.data.filter(f => ivIds.has(f.interview_id))

    documents.value = allDocs.data

    // Load status history for all applications
    const historyResults = await Promise.all(
      applications.value.map(a => api.get(`/applications/${a.id}/history`).then(r => r.data).catch(() => []))
    )
    statusHistory.value = historyResults.flat().sort((a, b) => new Date(b.changed_at) - new Date(a.changed_at))

    // Load notes
    try {
      const notesRes = await api.get(`/notes/candidate/${candidateId.value}`)
      notes.value = notesRes.data
    } catch {}
  } catch {}
  loading.value = false
})

async function addNote() {
  if (!newNote.value.trim()) return
  try {
    const res = await api.post('/notes/', { candidate_id: candidateId.value, text: newNote.value })
    notes.value.unshift(res.data)
    newNote.value = ''
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

async function deleteNote(id) {
  try {
    await api.delete(`/notes/${id}`)
    notes.value = notes.value.filter(n => n.id !== id)
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

function editInterview(iv) {
  selectedApplication.value = applications.value.find(a => a.id === iv.application_id) || { id: iv.application_id }
  selectedInterview.value = iv
  showInterviewModal.value = true
}

async function handleInterviewUpdated() {
  showInterviewModal.value = false
  const allInterviews = await api.get('/interviews/')
  const appIds = new Set(applications.value.map(a => a.id))
  interviews.value = allInterviews.data.filter(i => appIds.has(i.application_id))
}

async function cancelInterview(id) {
  if (!confirm('Вы уверены, что хотите отменить это собеседование?')) return
  try {
    await api.delete(`/interviews/${id}`)
    interviews.value = interviews.value.filter(i => i.id !== id)
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('ru-RU', { dateStyle: 'medium', timeStyle: 'short' })
}

function formatDateShort(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}

function initials(name) {
  if (!name) return '?'
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

function renderStars(score) {
  if (!score) return ''
  return '★'.repeat(score) + '☆'.repeat(5 - score)
}

const currentStatus = computed(() => {
  if (!applications.value.length) return null
  return applications.value[0]?.status
})
</script>

<template>
  <div class="h-full flex flex-col bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <!-- Header -->
    <div class="p-4 md:p-8 pb-4 flex items-center gap-4 border-b border-brand-light-border dark:border-brand-dark-border">
      <button @click="router.push('/hr')" class="p-2 rounded-xl hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated text-brand-light-muted dark:text-brand-dark-muted transition-colors">
        <ArrowLeft class="w-5 h-5" />
      </button>
      <div class="flex-1">
        <h1 class="text-xl font-bold text-brand-light-primary dark:text-brand-dark-primary">Карточка кандидата</h1>
        <p class="text-sm text-brand-light-secondary dark:text-brand-dark-secondary mt-0.5">{{ candidate?.full_name }}</p>
      </div>
      <span v-if="currentStatus" :class="['text-sm font-bold px-3 py-1.5 rounded-xl', STATUS_COLORS[currentStatus] || 'bg-gray-400/10 text-gray-400']">
        {{ STATUS_LABELS[currentStatus] || currentStatus }}
      </span>
    </div>

    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <Loader2 class="w-10 h-10 animate-spin text-brand-accent" />
    </div>

    <div v-else-if="candidate" class="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- LEFT: Profile info -->
        <div class="lg:col-span-2 space-y-6">

          <!-- Basic info -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6">
            <div class="flex items-start gap-4">
              <div class="w-16 h-16 rounded-2xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center shrink-0">
                <span class="text-2xl font-bold text-brand-accent">{{ initials(candidate.full_name) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <h2 class="text-xl font-bold text-brand-light-primary dark:text-brand-dark-primary">{{ candidate.full_name }}</h2>
                <p v-if="candidate.desired_position" class="text-brand-accent font-medium mt-0.5">{{ candidate.desired_position }}</p>
                <div class="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-sm text-brand-light-secondary dark:text-brand-dark-secondary">
                  <span v-if="candidate.email" class="flex items-center gap-1.5"><Mail class="w-3.5 h-3.5" />{{ candidate.email }}</span>
                  <span v-if="candidate.phone" class="flex items-center gap-1.5"><Phone class="w-3.5 h-3.5" />{{ candidate.phone }}</span>
                  <span v-if="candidate.city" class="flex items-center gap-1.5"><MapPin class="w-3.5 h-3.5" />{{ candidate.city }}</span>
                </div>
                <div class="flex flex-wrap gap-2 mt-3">
                  <span v-if="candidate.level" class="text-xs font-bold px-2.5 py-1 bg-brand-accent/10 text-brand-accent rounded-lg">{{ candidate.level }}</span>
                  <span v-if="candidate.work_format" class="text-xs font-bold px-2.5 py-1 bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary rounded-lg">{{ candidate.work_format }}</span>
                  <span v-if="candidate.employment_type" class="text-xs font-bold px-2.5 py-1 bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary rounded-lg">{{ candidate.employment_type }}</span>
                  <span v-if="candidate.salary_from || candidate.salary_to" class="text-xs font-bold px-2.5 py-1 bg-emerald-500/10 text-emerald-500 rounded-lg flex items-center gap-1">
                    <DollarSign class="w-3 h-3" />
                    {{ candidate.salary_from ? candidate.salary_from.toLocaleString() : '—' }} – {{ candidate.salary_to ? candidate.salary_to.toLocaleString() : '—' }} ₽
                  </span>
                </div>
              </div>
            </div>

            <!-- Links -->
            <div v-if="candidate.linkedin || candidate.github || candidate.portfolio" class="flex flex-wrap gap-3 mt-4 pt-4 border-t border-brand-light-border dark:border-brand-dark-border">
              <a v-if="candidate.linkedin" :href="candidate.linkedin" target="_blank" class="flex items-center gap-1.5 text-xs font-bold text-brand-accent hover:underline">
                <Globe class="w-3.5 h-3.5" /> LinkedIn
              </a>
              <a v-if="candidate.github" :href="candidate.github" target="_blank" class="flex items-center gap-1.5 text-xs font-bold text-brand-accent hover:underline">
                <Github class="w-3.5 h-3.5" /> GitHub
              </a>
              <a v-if="candidate.portfolio" :href="candidate.portfolio" target="_blank" class="flex items-center gap-1.5 text-xs font-bold text-brand-accent hover:underline">
                <Link class="w-3.5 h-3.5" /> Портфолио
              </a>
            </div>
          </div>

          <!-- Skills -->
          <div v-if="candidate.skills" class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6">
            <h3 class="text-sm font-bold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-3">Навыки</h3>
            <div class="flex flex-wrap gap-2">
              <span v-for="skill in candidate.skills.split(',')" :key="skill" class="text-sm bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-primary dark:text-brand-dark-primary px-3 py-1.5 rounded-lg border border-brand-light-border dark:border-brand-dark-border">
                {{ skill.trim() }}
              </span>
            </div>
          </div>

          <!-- Experience -->
          <div v-if="candidate.experience" class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6">
            <h3 class="text-sm font-bold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-3">Опыт работы</h3>
            <p class="text-body text-brand-light-primary dark:text-brand-dark-primary whitespace-pre-line">{{ candidate.experience }}</p>
          </div>

          <!-- Reviews / Feedbacks -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6">
            <h3 class="text-sm font-bold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-4 flex items-center gap-2">
              <MessageSquare class="w-4 h-4" /> Отзывы руководителей ({{ feedbacks.length }})
            </h3>
            <div v-if="!feedbacks.length" class="text-caption text-brand-light-muted dark:text-brand-dark-muted text-center py-4">Отзывов пока нет</div>
            <div class="space-y-4">
              <div v-for="fb in feedbacks" :key="fb.id" class="p-4 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-xl space-y-3">
                <div class="flex items-start justify-between gap-2">
                  <div class="grid grid-cols-2 gap-x-6 gap-y-1 text-xs">
                    <span v-if="fb.score_overall" class="text-brand-light-secondary dark:text-brand-dark-secondary">Общая: <span class="text-yellow-400 font-bold">{{ renderStars(fb.score_overall) }}</span></span>
                    <span v-if="fb.score_technical" class="text-brand-light-secondary dark:text-brand-dark-secondary">Знания: <span class="text-yellow-400 font-bold">{{ renderStars(fb.score_technical) }}</span></span>
                    <span v-if="fb.score_communication" class="text-brand-light-secondary dark:text-brand-dark-secondary">Коммуникация: <span class="text-yellow-400 font-bold">{{ renderStars(fb.score_communication) }}</span></span>
                    <span v-if="fb.score_fit" class="text-brand-light-secondary dark:text-brand-dark-secondary">Соответствие: <span class="text-yellow-400 font-bold">{{ renderStars(fb.score_fit) }}</span></span>
                  </div>
                  <div class="shrink-0 text-right">
                    <span v-if="fb.recommendation" :class="['text-xs font-bold', REC_COLORS[fb.recommendation]]">{{ REC_LABELS[fb.recommendation] }}</span>
                    <p class="text-micro text-brand-light-muted dark:text-brand-dark-muted mt-0.5">{{ formatDateShort(fb.created_at) }}</p>
                  </div>
                </div>
                <div v-if="fb.strengths || fb.weaknesses" class="grid grid-cols-2 gap-3">
                  <div v-if="fb.strengths" class="text-xs">
                    <p class="font-bold text-emerald-500 mb-1">+ Сильные стороны</p>
                    <p class="text-brand-light-secondary dark:text-brand-dark-secondary">{{ fb.strengths }}</p>
                  </div>
                  <div v-if="fb.weaknesses" class="text-xs">
                    <p class="font-bold text-red-400 mb-1">- Слабые стороны</p>
                    <p class="text-brand-light-secondary dark:text-brand-dark-secondary">{{ fb.weaknesses }}</p>
                  </div>
                </div>
                <p v-if="fb.text" class="text-sm text-brand-light-primary dark:text-brand-dark-primary">{{ fb.text }}</p>
              </div>
            </div>
          </div>

          <!-- HR Notes -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6">
            <h3 class="text-sm font-bold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-4 flex items-center gap-2">
              <StickyNote class="w-4 h-4" /> Внутренние заметки ({{ notes.length }})
            </h3>
            <div class="flex gap-2 mb-4">
              <input
                v-model="newNote"
                @keyup.enter="addNote"
                type="text"
                placeholder="Добавить заметку..."
                class="flex-1 bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-3 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent"
              />
              <button @click="addNote" class="px-3 py-2 bg-brand-accent text-white rounded-xl text-sm font-bold hover:opacity-90 transition-opacity">
                <Plus class="w-4 h-4" />
              </button>
            </div>
            <div v-if="!notes.length" class="text-caption text-brand-light-muted dark:text-brand-dark-muted text-center py-2">Заметок нет</div>
            <div class="space-y-2">
              <div v-for="note in notes" :key="note.id" class="p-3 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-xl flex items-start gap-3">
                <div class="flex-1">
                  <p class="text-sm text-brand-light-primary dark:text-brand-dark-primary">{{ note.text }}</p>
                  <p class="text-micro text-brand-light-muted dark:text-brand-dark-muted mt-1">{{ formatDateShort(note.created_at) }}</p>
                </div>
                <button @click="deleteNote(note.id)" class="p-1 text-red-400 hover:bg-red-400/10 rounded transition-colors shrink-0">
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          <!-- Status History -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-6">
            <h3 class="text-sm font-bold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-4 flex items-center gap-2">
              <Clock class="w-4 h-4" /> История статусов
            </h3>
            <div v-if="!statusHistory.length" class="text-caption text-brand-light-muted dark:text-brand-dark-muted text-center py-4">История пуста</div>
            <div class="space-y-2">
              <div v-for="h in statusHistory" :key="h.id" class="flex items-center gap-3 text-sm">
                <div class="w-2 h-2 rounded-full bg-brand-accent shrink-0"></div>
                <span class="text-brand-light-muted dark:text-brand-dark-muted text-xs shrink-0">{{ formatDateShort(h.changed_at) }}</span>
                <span v-if="h.from_status" class="text-brand-light-muted dark:text-brand-dark-muted">{{ STATUS_LABELS[h.from_status] || h.from_status }}</span>
                <span v-if="h.from_status" class="text-brand-light-muted">→</span>
                <span :class="['font-medium', STATUS_COLORS[h.to_status]?.split(' ')[1] || 'text-brand-light-primary dark:text-brand-dark-primary']">{{ STATUS_LABELS[h.to_status] || h.to_status }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT: Documents + Interviews -->
        <div class="space-y-6">

          <!-- Resume -->
          <div v-if="candidate.resume_url" class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <h3 class="text-sm font-bold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-3">Резюме</h3>
            <a :href="candidate.resume_url" target="_blank" class="flex items-center gap-2 p-3 bg-brand-accent/5 border border-brand-accent/20 rounded-xl text-brand-accent font-medium text-sm hover:bg-brand-accent/10 transition-colors">
              <FileText class="w-4 h-4" />
              Открыть резюме
              <ExternalLink class="w-4 h-4 ml-auto" />
            </a>
          </div>

          <!-- Documents -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <h3 class="text-sm font-bold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-3">Документы ({{ documents.length }})</h3>
            <div v-if="!documents.length" class="text-caption text-brand-light-muted dark:text-brand-dark-muted text-center py-3">Документы не загружены</div>
            <div class="space-y-2">
              <a
                v-for="doc in documents"
                :key="doc.id"
                :href="doc.url"
                target="_blank"
                class="flex items-center gap-2 p-2.5 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-xl hover:bg-brand-accent/5 transition-colors group"
              >
                <FileText class="w-4 h-4 text-brand-accent shrink-0" />
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-brand-light-primary dark:text-brand-dark-primary truncate">{{ doc.name }}</p>
                  <p class="text-xs text-brand-light-muted dark:text-brand-dark-muted">{{ DOC_LABELS[doc.doc_type] || doc.doc_type }}</p>
                </div>
                <ExternalLink class="w-3.5 h-3.5 text-brand-accent opacity-0 group-hover:opacity-100 transition-opacity" />
              </a>
            </div>
          </div>

          <!-- Interviews -->
          <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-5">
            <h3 class="text-sm font-bold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-3">Собеседования ({{ interviews.length }})</h3>
            <div v-if="!interviews.length" class="text-caption text-brand-light-muted dark:text-brand-dark-muted text-center py-3">Собеседований нет</div>
            <div class="space-y-2">
              <div v-for="iv in interviews" :key="iv.id" class="p-3 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-xl">
                <div class="flex items-start justify-between">
                  <div>
                    <div class="flex items-center gap-2 text-xs font-bold text-brand-status-interview">
                      <Calendar class="w-3.5 h-3.5" />
                      {{ formatDate(iv.scheduled_at) }}
                    </div>
                    <div v-if="iv.format" class="text-xs text-brand-light-muted dark:text-brand-dark-muted mt-1">{{ FORMAT_LABELS[iv.format] || iv.format }}</div>
                    <div v-if="iv.location" class="text-xs text-brand-light-muted dark:text-brand-dark-muted">📍 {{ iv.location }}</div>
                    <div v-if="iv.comment" class="text-xs text-brand-light-secondary dark:text-brand-dark-secondary mt-1 italic">{{ iv.comment }}</div>
                  </div>
                  <div class="flex items-center gap-1">
                    <button @click="editInterview(iv)" class="p-1.5 text-brand-light-muted hover:text-brand-accent hover:bg-brand-accent/10 rounded-lg transition-colors" title="Изменить">
                      <Edit2 class="w-3.5 h-3.5" />
                    </button>
                    <button @click="cancelInterview(iv.id)" class="p-1.5 text-brand-light-muted hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors" title="Отменить">
                      <XCircle class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Interview Edit Modal -->
    <Teleport to="body">
      <InterviewModal
        v-if="showInterviewModal"
        :application="selectedApplication"
        :interview="selectedInterview"
        @close="showInterviewModal = false"
        @updated="handleInterviewUpdated"
      />
    </Teleport>
  </div>
</template>
