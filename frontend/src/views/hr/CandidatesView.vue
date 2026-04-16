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
} from 'lucide-vue-next'

const router = useRouter()

const STATUSES = ['new', 'screening', 'interview', 'hired', 'rejected']

const columns = [
  { key: 'new',       label: 'Новые',    dot: 'bg-brand-status-new',       badge: 'bg-brand-status-new/10 text-brand-status-new',       top: 'border-t-brand-status-new' },
  { key: 'screening', label: 'Скрининг', dot: 'bg-brand-status-screening', badge: 'bg-brand-status-screening/10 text-brand-status-screening', top: 'border-t-brand-status-screening' },
  { key: 'interview', label: 'Интервью', dot: 'bg-brand-status-interview', badge: 'bg-brand-status-interview/10 text-brand-status-interview', top: 'border-t-brand-status-interview' },
  { key: 'hired',     label: 'Нанят',    dot: 'bg-brand-status-hired',     badge: 'bg-brand-status-hired/10 text-brand-status-hired',     top: 'border-t-brand-status-hired' },
  { key: 'rejected',  label: 'Отказ',    dot: 'bg-brand-status-rejected',  badge: 'bg-brand-status-rejected/10 text-brand-status-rejected',  top: 'border-t-brand-status-rejected' },
]

const colApps = ref({
  new: [], screening: [], interview: [], hired: [], rejected: [],
})
const candidates = ref([])
const interviews = ref([])
const search = ref('')
const allApps = ref([])
const loading = ref(true)
const showModal = ref(false)
const selectedApp = ref(null)
const activeMenu = ref(null)
const menuEl = ref(null)

onMounted(loadData)

async function loadData() {
  console.log('[CandidatesView] Starting data load...')
  loading.value = true
  try {
    const [appsRes, candidatesRes, interviewsRes] = await Promise.all([
      api.get('/applications/'),
      api.get('/candidates/'),
      api.get('/interviews/'),
    ])
    console.log('[CandidatesView] Data loaded:', appsRes.data.length, 'apps,', candidatesRes.data.length, 'candidates')
    candidates.value = candidatesRes.data
    allApps.value = appsRes.data
    interviews.value = interviewsRes.data
    updateColApps()
  } catch (err) {
    console.error('[CandidatesView] Load error:', err)
  } finally {
    loading.value = false
  }
}

function updateColApps() {
  console.log('[CandidatesView] Updating column filtered lists...')
  if (!allApps.value) return
  for (const status of STATUSES) {
    colApps.value[status] = allApps.value.filter((a) => {
      if (a.status !== status) return false
      if (!search.value) return true
      const cand = candidateForApp(a)
      const q = search.value.toLowerCase()
      const matchText = cand?.full_name?.toLowerCase().includes(q) || cand?.email?.toLowerCase().includes(q)
      return matchText
    })
  }
}

import { watch, onUnmounted } from 'vue'
watch(search, updateColApps)

// Close menu when clicking outside
const closeMenuHandler = () => { activeMenu.value = null }
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
    <div class="p-4 md:p-8 pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
          <Users class="w-7 h-7 text-brand-accent" />
          Управление кандидатами
        </h1>
        <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Организуйте процесс подбора и меняйте этапы откликов</p>
      </div>
      
      <div class="flex items-center gap-3 w-full md:w-auto">
        <div class="relative flex-1 md:flex-none">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted" />
          <input
            v-model="search"
            type="text"
            placeholder="Поиск..."
            class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/5 transition-all w-full md:w-72"
          />
        </div>
        <button class="p-2.5 rounded-xl border border-brand-light-border dark:border-brand-dark-border bg-brand-light-surface dark:bg-brand-dark-surface text-brand-light-secondary dark:text-brand-dark-secondary hover:text-brand-light-primary dark:hover:text-brand-dark-primary transition-all">
          <Filter class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Kanban board -->
    <div class="flex-1 p-4 md:p-8 pt-4 overflow-x-auto custom-scrollbar-h">
      <div v-if="loading" class="flex items-center justify-center h-64">
        <Loader2 class="w-10 h-10 animate-spin text-brand-accent" />
      </div>
      
      <div v-else class="flex gap-6 h-full min-w-max pb-4">
        <div
          v-for="col in columns"
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
                    <h4 class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-sm leading-tight truncate">
                      {{ candidateForApp(app)?.full_name || 'Кандидат #' + app.candidate_id }}
                    </h4>
                    <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary mt-0.5 truncate flex items-center gap-1">
                      <Mail class="w-3 h-3" />
                      {{ candidateForApp(app)?.email }}
                    </p>
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
                    class="absolute right-0 mt-2 w-48 bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl shadow-xl z-10 py-2 antialiased"
                  >
                    <button 
                      @click="openInterviewModal(app)"
                      class="w-full text-left px-4 py-2 text-sm text-brand-light-primary dark:text-brand-dark-primary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated flex items-center gap-2"
                    >
                      <Calendar class="w-4 h-4" /> Назначить интервью
                    </button>
                    <button 
                      v-if="app.status !== 'rejected'"
                      @click="updateAppStatus(app, 'rejected')"
                      class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-red-500/5 flex items-center gap-2"
                    >
                      <X class="w-4 h-4" /> Отклонить
                    </button>
                    <div class="h-px bg-brand-light-border dark:bg-brand-dark-border my-1"></div>
                    <a 
                      :href="`mailto:${candidateForApp(app)?.email}`"
                      class="w-full text-left px-4 py-2 text-sm text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated flex items-center gap-2"
                    >
                      <Mail class="w-4 h-4" /> Написать письмо
                    </a>
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
                  class="flex items-center gap-1.5 text-micro font-bold text-brand-accent hover:text-brand-accent-hover transition-colors"
                >
                  <FileText class="w-3.5 h-3.5" />
                  РЕЗЮМЕ
                </a>
                
                <template v-if="app.status === 'interview'">
                  <button
                    v-if="interviewForApp(app)"
                    @click="router.push(`/call/${interviewForApp(app).room_code}`)"
                    class="flex items-center gap-1 text-micro font-bold text-brand-status-interview hover:opacity-80 transition-opacity uppercase"
                  >
                    <Video class="w-3.5 h-3.5" />
                    Войти
                  </button>
                  <button
                    v-else
                    @click="openInterviewModal(app)"
                    class="flex items-center gap-1 text-micro font-bold text-brand-status-interview hover:opacity-80 transition-opacity uppercase"
                  >
                    <Calendar class="w-3.5 h-3.5" />
                    Запись
                  </button>
                </template>
              </div>
            </div>
          </VueDraggable>
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
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #2a2f4a;
}
</style>
