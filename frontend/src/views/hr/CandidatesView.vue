<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VueDraggable } from 'vue-draggable-plus'
import api from '@/api/index.js'
import AppLayout from '@/components/AppLayout.vue'
import InterviewModal from './InterviewModal.vue'
import {
  Users,
  Search,
  Filter,
  FileText,
  ExternalLink,
  Calendar,
  Plus,
  Loader2,
  MoreHorizontal,
  Mail,
  X,
  Video,
  SlidersHorizontal,
} from 'lucide-vue-next'

const router = useRouter()

const STATUSES = [
  'new', 'screening', 'interview', 'manager_interview',
  'interview_done', 'awaiting_decision', 'reserve', 'offer',
  'hired', 'rejected', 'accepted',
]

const ARCHIVE_STATUSES = ['hired', 'rejected', 'accepted']

const columns = [
  { key: 'new',               label: 'Новый',                dot: 'bg-blue-400',    badge: 'bg-blue-400/10 text-blue-400',    top: 'border-t-blue-400' },
  { key: 'screening',         label: 'На рассмотрении',      dot: 'bg-yellow-400',  badge: 'bg-yellow-400/10 text-yellow-400', top: 'border-t-yellow-400' },
  { key: 'interview',         label: 'HR-интервью',          dot: 'bg-purple-400',  badge: 'bg-purple-400/10 text-purple-400', top: 'border-t-purple-400' },
  { key: 'manager_interview', label: 'Интервью с руковод.',  dot: 'bg-indigo-400',  badge: 'bg-indigo-400/10 text-indigo-400', top: 'border-t-indigo-400' },
  { key: 'interview_done',    label: 'Интервью проведено',   dot: 'bg-cyan-400',    badge: 'bg-cyan-400/10 text-cyan-400',    top: 'border-t-cyan-400' },
  { key: 'awaiting_decision', label: 'Ожидает решения',      dot: 'bg-orange-400',  badge: 'bg-orange-400/10 text-orange-400', top: 'border-t-orange-400' },
  { key: 'reserve',           label: 'Резерв',               dot: 'bg-teal-400',    badge: 'bg-teal-400/10 text-teal-400',    top: 'border-t-teal-400' },
  { key: 'offer',             label: 'Оффер',                dot: 'bg-emerald-400', badge: 'bg-emerald-400/10 text-emerald-400', top: 'border-t-emerald-400' },
]

const archiveColumns = [
  { key: 'hired',    label: 'Нанят',  dot: 'bg-green-500', badge: 'bg-green-500/10 text-green-500',  top: 'border-t-green-500' },
  { key: 'rejected', label: 'Отказ',  dot: 'bg-red-400',   badge: 'bg-red-400/10 text-red-400',      top: 'border-t-red-400' },
  { key: 'accepted', label: 'Принят', dot: 'bg-green-600', badge: 'bg-green-600/10 text-green-600',  top: 'border-t-green-600' },
]

const colApps = ref({
  new: [], screening: [], interview: [], manager_interview: [],
  interview_done: [], awaiting_decision: [], reserve: [], offer: [],
  hired: [], rejected: [], accepted: [],
})
const candidates = ref([])
const interviews = ref([])
const vacancies = ref([])
const search = ref('')
const filterStatus = ref('') // '' = all, or specific status key
const filterVacancy = ref('') // '' = all, or vacancy id (as string)
const showFilterMenu = ref(false)
const showExtendedFilters = ref(false)
const showEmptyColumns = ref(false)
const showArchive = ref(false)
const allApps = ref([])
const loading = ref(true)
const showModal = ref(false)
const selectedApp = ref(null)
const activeMenu = ref(null)
const menuEl = ref(null)
const filterSkills = ref('')
const filterCity = ref('')
const filterLevel = ref('')
const filterWorkFormat = ref('')
const filterSalaryMin = ref('')
const filterSalaryMax = ref('')

onMounted(loadData)

async function loadData() {
  console.log('[CandidatesView] Starting data load...')
  loading.value = true
  try {
    const [appsRes, candidatesRes, interviewsRes, vacRes] = await Promise.all([
      api.get('/applications/'),
      api.get('/candidates/'),
      api.get('/interviews/'),
      api.get('/vacancies/'),
    ])
    console.log('[CandidatesView] Data loaded:', appsRes.data.length, 'apps,', candidatesRes.data.length, 'candidates')
    candidates.value = candidatesRes.data
    allApps.value = appsRes.data
    interviews.value = interviewsRes.data
    vacancies.value = vacRes.data
    updateColApps()
  } catch (err) {
    console.error('[CandidatesView] Load error:', err)
  } finally {
    loading.value = false
  }
}

function updateColApps() {
  if (!allApps.value) return
  for (const status of STATUSES) {
    colApps.value[status] = allApps.value.filter((a) => {
      if (a.status !== status) return false
      if (filterStatus.value && a.status !== filterStatus.value) return false
      if (filterVacancy.value && String(a.vacancy_id) !== filterVacancy.value) return false
      const cand = candidateForApp(a)
      if (!matchesExtendedFilters(cand)) return false
      if (search.value) {
        const q = search.value.toLowerCase()
        return cand?.full_name?.toLowerCase().includes(q) || cand?.email?.toLowerCase().includes(q)
      }
      return true
    })
  }
}

import { watch, computed, onUnmounted } from 'vue'
watch([search, filterStatus, filterVacancy, filterSkills, filterCity, filterLevel, filterWorkFormat, filterSalaryMin, filterSalaryMax], updateColApps)

function matchesExtendedFilters(cand) {
  if (!cand) return true
  if (filterSkills.value && !(cand.skills || '').toLowerCase().includes(filterSkills.value.toLowerCase())) return false
  if (filterCity.value && !(cand.city || '').toLowerCase().includes(filterCity.value.toLowerCase())) return false
  if (filterLevel.value && cand.level !== filterLevel.value) return false
  if (filterWorkFormat.value && !(cand.work_format || '').toLowerCase().includes(filterWorkFormat.value.toLowerCase())) return false
  if (filterSalaryMin.value && (cand.salary_from || 0) < Number(filterSalaryMin.value)) return false
  if (filterSalaryMax.value && (cand.salary_to || 999999999) > Number(filterSalaryMax.value)) return false
  return true
}

const visibleColumns = computed(() =>
  showEmptyColumns.value
    ? columns
    : columns.filter(col => colApps.value[col.key].length > 0)
)

const archiveTotal = computed(() =>
  ARCHIVE_STATUSES.reduce((sum, s) => sum + (colApps.value[s]?.length || 0), 0)
)

const pipelineTotal = computed(() =>
  columns.reduce((sum, col) => sum + (colApps.value[col.key]?.length || 0), 0)
)

// Close menus when clicking outside
const closeMenuHandler = () => { activeMenu.value = null; showFilterMenu.value = false }
onMounted(() => window.addEventListener('click', closeMenuHandler))
onUnmounted(() => window.removeEventListener('click', closeMenuHandler))

function candidateForApp(app) {
  return candidates.value.find((c) => c.id === app.candidate_id)
}

function interviewForApp(app) {
  return interviews.value.find((i) => i.application_id === app.id)
}

function initials(name) {
  if (!name) return '?'
  return name.split(' ').slice(0, 2).map((w) => w[0]).join('').toUpperCase()
}

function vacancyTitle(vacancyId) {
  return vacancies.value.find(v => v.id === vacancyId)?.title || null
}

function formatDate(dt) {
  if (!dt) return null
  return new Date(dt).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

async function onColAdd(status, event) {
  // Use the index provided by Sortable to find the item in our reactive array
  const app = colApps.value[status][event.newIndex]
  if (!app) {
    console.error('No item found at index:', event.newIndex, 'in column:', status)
    return
  }
  
  console.log(`[Kanban] Moving app ${app.id} to stage: ${status}`)
  
  // Update local application status
  app.status = status
  
  // Sync allApps to keep search/filter working correctly (since it's the source for updateColApps)
  const idx = allApps.value.findIndex(a => a.id === app.id)
  if (idx !== -1) {
    allApps.value[idx].status = status
  }

  try {
    await api.put(`/applications/${app.id}/status`, { status })
    console.log(`[Kanban] Successfully updated ${app.id} to ${status}`)
  } catch (err) {
    console.error('[Kanban] API Error:', err)
    // Reload to ensure UI matches server state on failure
    await loadData()
  }
}

function openInterviewModal(app) {
  selectedApp.value = app
  showModal.value = true
  activeMenu.value = null
}

function toggleMenu(appId) {
  activeMenu.value = activeMenu.value === appId ? null : appId
}

async function updateAppStatus(app, newStatus) {
  activeMenu.value = null
  app.status = newStatus
  
  // Update in allApps
  const idx = allApps.value.findIndex(a => a.id === app.id)
  if (idx !== -1) allApps.value[idx].status = newStatus
  
  // Re-filter columns
  updateColApps()
  
  try {
    await api.put(`/applications/${app.id}/status`, { status: newStatus })
  } catch (err) {
    await loadData()
  }
}
</script>

<template>
  <div class="h-full flex flex-col bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <div class="p-4 md:p-8 pb-4 flex flex-col gap-4">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
            <Users class="w-7 h-7 text-brand-accent" />
            Управление кандидатами
          </h1>
          <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Организуйте процесс подбора и меняйте этапы откликов</p>
        </div>
        
        <div class="flex items-center gap-3 w-full md:w-auto flex-wrap">
          <div class="relative flex-1 md:flex-none">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted" />
            <input
              v-model="search"
              type="text"
              placeholder="Поиск..."
              class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/5 transition-all w-full md:w-64"
            />
          </div>

          <select
            v-if="vacancies.length > 0"
            v-model="filterVacancy"
            class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-3 py-2.5 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent transition-all appearance-none"
            :class="filterVacancy ? 'border-brand-accent text-brand-accent' : ''"
          >
            <option value="">Все вакансии</option>
            <option v-for="v in vacancies" :key="v.id" :value="String(v.id)">{{ v.title }}</option>
          </select>
          <button
            @click="showExtendedFilters = !showExtendedFilters"
            :class="[
              'p-2.5 rounded-xl border bg-brand-light-surface dark:bg-brand-dark-surface transition-all flex items-center gap-2 text-sm',
              showExtendedFilters || filterSkills || filterCity || filterLevel || filterWorkFormat || filterSalaryMin || filterSalaryMax
                ? 'border-brand-accent text-brand-accent'
                : 'border-brand-light-border dark:border-brand-dark-border text-brand-light-secondary dark:text-brand-dark-secondary hover:text-brand-light-primary dark:hover:text-brand-dark-primary'
            ]"
          >
            <SlidersHorizontal class="w-4.5 h-4.5" />
            <span class="hidden md:inline">Фильтры</span>
          </button>
          <select
            v-model="filterStatus"
            class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl px-3 py-2.5 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent transition-all appearance-none"
            :class="filterStatus ? 'border-brand-accent text-brand-accent' : ''"
          >
            <option value="">Все этапы</option>
            <option v-for="col in columns" :key="col.key" :value="col.key">{{ col.label }}</option>
          </select>
          <button
            @click="showEmptyColumns = !showEmptyColumns"
            :class="[
              'p-2.5 rounded-xl border bg-brand-light-surface dark:bg-brand-dark-surface transition-all text-xs font-bold whitespace-nowrap px-3',
              showEmptyColumns
                ? 'border-brand-accent text-brand-accent'
                : 'border-brand-light-border dark:border-brand-dark-border text-brand-light-secondary dark:text-brand-dark-secondary hover:text-brand-light-primary dark:hover:text-brand-dark-primary'
            ]"
          >
            {{ showEmptyColumns ? 'Скрыть пустые' : 'Показать пустые' }}
          </button>
        </div>
      </div>

      <!-- Extended Filters Row -->
      <div v-show="showExtendedFilters" class="flex items-center gap-2 flex-wrap bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl p-3 w-full shadow-sm">
        <input v-model="filterSkills" type="text" placeholder="Навыки (напр. Python)..." class="bg-brand-light-base dark:bg-brand-dark-base border border-brand-light-border dark:border-brand-dark-border rounded-xl px-3 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent flex-1 min-w-[140px]" />
        <input v-model="filterCity" type="text" placeholder="Город..." class="bg-brand-light-base dark:bg-brand-dark-base border border-brand-light-border dark:border-brand-dark-border rounded-xl px-3 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent flex-1 md:flex-none w-full md:w-32" />
        <select v-model="filterLevel" class="bg-brand-light-base dark:bg-brand-dark-base border border-brand-light-border dark:border-brand-dark-border rounded-xl px-3 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent appearance-none flex-1 md:flex-none w-full md:w-32" :class="filterLevel ? 'border-brand-accent' : ''">
          <option value="">Уровень</option>
          <option value="junior">Junior</option>
          <option value="middle">Middle</option>
          <option value="senior">Senior</option>
          <option value="lead">Lead</option>
        </select>
        <input v-model="filterWorkFormat" type="text" placeholder="Формат..." class="bg-brand-light-base dark:bg-brand-dark-base border border-brand-light-border dark:border-brand-dark-border rounded-xl px-3 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent flex-1 md:flex-none w-full md:w-32" />
        <div class="flex items-center gap-2 flex-1 md:flex-none min-w-[180px]">
          <input v-model="filterSalaryMin" type="number" placeholder="ЗП от" class="bg-brand-light-base dark:bg-brand-dark-base border border-brand-light-border dark:border-brand-dark-border rounded-xl px-3 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent w-full" />
          <span class="text-brand-light-muted dark:text-brand-dark-muted">-</span>
          <input v-model="filterSalaryMax" type="number" placeholder="ЗП до" class="bg-brand-light-base dark:bg-brand-dark-base border border-brand-light-border dark:border-brand-dark-border rounded-xl px-3 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent w-full" />
        </div>
      </div>
    </div>

    <!-- Pipeline summary bar -->
    <div v-if="!loading && pipelineTotal > 0" class="px-4 md:px-8 pb-3 flex items-center gap-2 overflow-x-auto custom-scrollbar-h">
      <div
        v-for="col in columns.filter(c => colApps[c.key].length > 0)"
        :key="col.key"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-full border cursor-default shrink-0 transition-all hover:opacity-80"
        :class="col.badge + ' border-current/20'"
      >
        <span :class="['w-1.5 h-1.5 rounded-full', col.dot]"></span>
        <span class="text-xs font-bold">{{ col.label }}</span>
        <span class="text-xs font-black opacity-70">{{ colApps[col.key].length }}</span>
      </div>
      <div v-if="archiveTotal > 0" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-brand-light-border dark:border-brand-dark-border text-brand-light-secondary dark:text-brand-dark-secondary shrink-0">
        <span class="text-xs font-bold">Архив</span>
        <span class="text-xs font-black opacity-70">{{ archiveTotal }}</span>
      </div>
    </div>

    <!-- Kanban board -->
    <div class="flex-1 p-4 md:p-8 pt-0 overflow-x-auto custom-scrollbar-h">
      <div v-if="loading" class="flex items-center justify-center h-64">
        <Loader2 class="w-10 h-10 animate-spin text-brand-accent" />
      </div>
      
      <div v-else-if="visibleColumns.length === 0" class="flex flex-col items-center justify-center h-64 gap-4 text-center">
        <div class="w-16 h-16 rounded-2xl bg-brand-light-elevated dark:bg-brand-dark-elevated flex items-center justify-center">
          <Users class="w-8 h-8 text-brand-light-muted dark:text-brand-dark-muted" />
        </div>
        <div>
          <p class="text-body font-semibold text-brand-light-primary dark:text-brand-dark-primary">Кандидатов нет</p>
          <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Пока нет ни одной заявки</p>
        </div>
      </div>

      <div v-else class="flex gap-6 h-full min-w-max pb-4">
        <div
          v-for="col in visibleColumns"
          :key="col.key"
          class="w-[260px] flex flex-col h-full shrink-0"
        >
          <!-- Column header -->
          <div class="flex items-center justify-between mb-4 px-2">
            <div class="flex items-center gap-2.5">
              <div :class="['w-2 h-2 rounded-full', col.dot, 'shadow-[0_0_8px_rgba(0,0,0,0.1)]']" :style="{ '--tw-shadow-color': col.dot.replace('bg-', '') }"></div>
              <span class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-sm uppercase tracking-wider">{{ col.label }}</span>
            </div>
            <span :class="['text-micro rounded-lg px-2 py-0.5 font-bold', col.badge]">
              {{ colApps[col.key].length }}
            </span>
          </div>

          <!-- Draggable column -->
          <VueDraggable
            v-model="colApps[col.key]"
            :group="{ name: 'kanban' }"
            :animation="250"
            @add="(e) => onColAdd(col.key, e)"
            class="flex-1 overflow-y-auto min-h-[50vh] rounded-2xl border border-brand-light-border dark:border-brand-dark-border bg-brand-light-elevated/40 dark:bg-brand-dark-elevated/20 p-3 space-y-3 custom-scrollbar"
            :class="[col.top, 'border-t-[3px]']"
          >

            <div
              v-for="app in colApps[col.key]"
              :key="app.id"
              class="group bg-brand-light-surface dark:bg-brand-dark-surface rounded-2xl border border-brand-light-border dark:border-brand-dark-border p-4 cursor-grab active:cursor-grabbing hover:shadow-xl hover:shadow-brand-accent/5 hover:-translate-y-1 transition-all duration-300"
            >
              <!-- Avatar + name -->
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-start gap-3 min-w-0">
                  <div class="w-10 h-10 rounded-xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center shrink-0">
                    <span class="text-brand-accent text-sm font-bold">
                      {{ initials(candidateForApp(app)?.full_name) }}
                    </span>
                  </div>
                  <div class="min-w-0">
                    <h4
                      @click.stop="router.push(`/hr/candidates/${app.candidate_id}`)"
                      class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-sm leading-tight truncate cursor-pointer hover:text-brand-accent transition-colors"
                    >
                      {{ candidateForApp(app)?.full_name || 'Кандидат #' + app.candidate_id }}
                    </h4>
                    <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary mt-0.5 truncate flex items-center gap-1">
                      <Mail class="w-3 h-3" />
                      {{ candidateForApp(app)?.email }}
                    </p>
                    <div class="flex items-center gap-2 mt-1 flex-wrap">
                      <span v-if="vacancyTitle(app.vacancy_id)" class="text-micro bg-brand-accent/10 text-brand-accent px-1.5 py-0.5 rounded font-medium truncate max-w-[140px]">
                        {{ vacancyTitle(app.vacancy_id) }}
                      </span>
                      <span v-if="app.created_at" class="text-micro text-brand-light-muted dark:text-brand-dark-muted">
                        {{ formatDate(app.created_at) }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="relative">
                  <button 
                    @click.stop="toggleMenu(app.id)"
                    class="p-1 opacity-0 group-hover:opacity-100 transition-opacity text-brand-light-muted dark:text-brand-dark-muted hover:text-brand-light-primary dark:hover:text-brand-dark-primary"
                  >
                    <MoreHorizontal class="w-4 h-4" />
                  </button>
                  
                  <!-- Dropdown Menu -->
                  <div
                    v-if="activeMenu === app.id"
                    class="absolute right-0 mt-2 w-56 bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl shadow-xl z-10 py-2 antialiased"
                  >
                    <button
                      @click="router.push(`/hr/candidates/${app.candidate_id}`); activeMenu = null"
                      class="w-full text-left px-4 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated flex items-center gap-2"
                    >
                      <ExternalLink class="w-4 h-4" /> Открыть карточку
                    </button>
                    <button
                      v-if="!interviewForApp(app)"
                      @click="openInterviewModal(app)"
                      class="w-full text-left px-4 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated flex items-center gap-2"
                    >
                      <Calendar class="w-4 h-4" /> Назначить интервью
                    </button>
                    <div
                      v-else
                      class="px-4 py-2 text-sm text-brand-light-muted dark:text-brand-dark-muted flex items-center gap-2"
                    >
                      <Calendar class="w-4 h-4" /> Интервью назначено
                    </div>
                    <div class="h-px bg-brand-light-border dark:bg-brand-dark-border my-1"></div>
                    <button
                      v-if="app.status !== 'screening'"
                      @click="updateAppStatus(app, 'screening')"
                      class="w-full text-left px-4 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated flex items-center gap-2"
                    >
                      → На рассмотрении
                    </button>
                    <button
                      v-if="app.status !== 'interview'"
                      @click="updateAppStatus(app, 'interview')"
                      class="w-full text-left px-4 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated flex items-center gap-2"
                    >
                      → HR-интервью
                    </button>
                    <button
                      v-if="app.status !== 'manager_interview'"
                      @click="updateAppStatus(app, 'manager_interview')"
                      class="w-full text-left px-4 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated flex items-center gap-2"
                    >
                      → Интервью с рук-лем
                    </button>
                    <button
                      v-if="app.status !== 'offer'"
                      @click="updateAppStatus(app, 'offer')"
                      class="w-full text-left px-4 py-2 text-sm text-emerald-500 hover:bg-emerald-500/5 flex items-center gap-2"
                    >
                      → Оффер
                    </button>
                    <button
                      v-if="app.status !== 'accepted'"
                      @click="updateAppStatus(app, 'accepted')"
                      class="w-full text-left px-4 py-2 text-sm text-green-500 hover:bg-green-500/5 flex items-center gap-2"
                    >
                      → Принят
                    </button>
                    <button
                      v-if="app.status !== 'reserve'"
                      @click="updateAppStatus(app, 'reserve')"
                      class="w-full text-left px-4 py-2 text-sm text-teal-500 hover:bg-teal-500/5 flex items-center gap-2"
                    >
                      → Резерв
                    </button>
                    <button
                      v-if="app.status !== 'rejected'"
                      @click="updateAppStatus(app, 'rejected')"
                      class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-red-500/5 flex items-center gap-2"
                    >
                      <X class="w-4 h-4" /> Отклонить
                    </button>
                    <div class="h-px bg-brand-light-border dark:bg-brand-dark-border my-1"></div>
                    <button
                      @click="router.push(`/chat?user=${candidateForApp(app)?.user_id}`); activeMenu = null"
                      class="w-full text-left px-4 py-2 text-sm text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated flex items-center gap-2"
                    >
                      <Mail class="w-4 h-4" /> Написать сообщение
                    </button>
                  </div>
                </div>
              </div>

              <!-- Skills -->
              <div v-if="candidateForApp(app)?.skills" class="mt-4">
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="skill in candidateForApp(app)?.skills.split(',').slice(0, 3)" :key="skill" class="text-micro bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary px-2 py-0.5 rounded-md border border-brand-light-border dark:border-brand-dark-border">
                    {{ skill.trim() }}
                  </span>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center justify-between mt-4 pt-4 border-t border-brand-light-border dark:border-brand-dark-border">
                <a
                  v-if="candidateForApp(app)?.resume_url"
                  :href="candidateForApp(app)?.resume_url"
                  target="_blank"
                  @click.stop
                  class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-brand-accent/10 text-xs font-bold text-brand-accent hover:bg-brand-accent/20 transition-colors"
                >
                  <FileText class="w-3.5 h-3.5" />
                  РЕЗЮМЕ
                </a>
                
                <template v-if="['interview', 'manager_interview'].includes(app.status)">
                  <button
                    v-if="interviewForApp(app)"
                    @click.stop="router.push(`/call/${interviewForApp(app).room_code}`)"
                    class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-brand-status-interview/10 text-xs font-bold text-brand-status-interview hover:bg-brand-status-interview/20 transition-colors uppercase"
                  >
                    <Video class="w-3.5 h-3.5" />
                    Войти
                  </button>
                  <button
                    v-else
                    @click.stop="openInterviewModal(app)"
                    class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-brand-status-interview/10 text-xs font-bold text-brand-status-interview hover:bg-brand-status-interview/20 transition-colors uppercase"
                  >
                    <Calendar class="w-3.5 h-3.5" />
                    Запись
                  </button>
                </template>
              </div>
            </div>
          </VueDraggable>
        </div>

        <!-- Archive panel -->
        <div class="flex flex-col h-full shrink-0 w-[260px]">
          <button
            @click="showArchive = !showArchive"
            class="flex items-center justify-between mb-4 px-2 w-full"
          >
            <div class="flex items-center gap-2.5">
              <div class="w-2 h-2 rounded-full bg-brand-light-muted dark:bg-brand-dark-muted"></div>
              <span class="font-bold text-brand-light-secondary dark:text-brand-dark-secondary text-sm uppercase tracking-wider">Архив</span>
            </div>
            <div class="flex items-center gap-2">
              <span v-if="archiveTotal > 0" class="text-micro rounded-lg px-2 py-0.5 font-bold bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary">
                {{ archiveTotal }}
              </span>
              <span class="text-brand-light-muted dark:text-brand-dark-muted text-xs">{{ showArchive ? '▲' : '▼' }}</span>
            </div>
          </button>

          <div v-if="showArchive" class="flex-1 space-y-4 overflow-y-auto custom-scrollbar">
            <div v-for="col in archiveColumns" :key="col.key">
              <div class="flex items-center gap-2 mb-2 px-1">
                <span :class="['w-1.5 h-1.5 rounded-full', col.dot]"></span>
                <span class="text-xs font-bold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider">{{ col.label }}</span>
                <span :class="['text-micro rounded px-1.5 py-0.5 font-bold ml-auto', col.badge]">{{ colApps[col.key].length }}</span>
              </div>
              <VueDraggable
                v-model="colApps[col.key]"
                :group="{ name: 'kanban' }"
                :animation="250"
                @add="(e) => onColAdd(col.key, e)"
                class="min-h-[60px] rounded-xl border border-brand-light-border dark:border-brand-dark-border bg-brand-light-elevated/40 dark:bg-brand-dark-elevated/20 p-2 space-y-2"
                :class="[col.top, 'border-t-2']"
              >
                <div
                  v-for="app in colApps[col.key]"
                  :key="app.id"
                  class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-xl border border-brand-light-border dark:border-brand-dark-border px-3 py-2 cursor-grab active:cursor-grabbing"
                >
                  <p class="text-xs font-bold text-brand-light-primary dark:text-brand-dark-primary truncate">
                    {{ candidateForApp(app)?.full_name || 'Кандидат #' + app.candidate_id }}
                  </p>
                  <p class="text-micro text-brand-light-muted dark:text-brand-dark-muted truncate mt-0.5">
                    {{ candidateForApp(app)?.email }}
                  </p>
                </div>
              </VueDraggable>
            </div>
          </div>

          <div v-else class="flex-1 rounded-2xl border border-dashed border-brand-light-border dark:border-brand-dark-border flex items-center justify-center">
            <p class="text-xs text-brand-light-muted dark:text-brand-dark-muted text-center px-4">
              {{ archiveTotal }} завершённых
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <InterviewModal
      v-if="showModal"
      :application="selectedApp"
      @close="showModal = false"
      @created="showModal = false; loadData()"
    />
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
.custom-scrollbar-h::-webkit-scrollbar {
  height: 4px;
}
.custom-scrollbar-h::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar-h::-webkit-scrollbar-thumb {
  background: #2a2f4a;
  border-radius: 10px;
}
</style>
