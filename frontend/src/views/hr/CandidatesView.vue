<script setup>
import { ref, onMounted } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import api from '@/api/index.js'
import AppLayout from '@/components/AppLayout.vue'
import InterviewModal from './InterviewModal.vue'

const STATUSES = ['new', 'screening', 'interview', 'hired', 'rejected']

const columns = [
  { key: 'new',       label: 'Новые',    dot: 'bg-blue-500',    badge: 'bg-blue-500/15 text-blue-400',    top: 'border-t-blue-500' },
  { key: 'screening', label: 'Скрининг', dot: 'bg-amber-500',   badge: 'bg-amber-500/15 text-amber-400',  top: 'border-t-amber-500' },
  { key: 'interview', label: 'Интервью', dot: 'bg-violet-500',  badge: 'bg-violet-500/15 text-violet-400', top: 'border-t-violet-500' },
  { key: 'hired',     label: 'Нанят',    dot: 'bg-emerald-500', badge: 'bg-emerald-500/15 text-emerald-400', top: 'border-t-emerald-500' },
  { key: 'rejected',  label: 'Отказ',    dot: 'bg-red-500',     badge: 'bg-red-500/15 text-red-400',      top: 'border-t-red-500' },
]

// Separate reactive array per column — needed for vue-draggable-plus v-model
const colApps = ref({
  new: [], screening: [], interview: [], hired: [], rejected: [],
})
const candidates = ref([])

const showModal = ref(false)
const selectedApp = ref(null)

onMounted(loadData)

async function loadData() {
  const [appsRes, candidatesRes] = await Promise.all([
    api.get('/applications/'),
    api.get('/candidates/'),
  ])
  candidates.value = candidatesRes.data
  for (const status of STATUSES) {
    colApps.value[status] = appsRes.data.filter((a) => a.status === status)
  }
}

function candidateForApp(app) {
  return candidates.value.find((c) => c.id === app.candidate_id)
}

function initials(name) {
  if (!name) return '?'
  return name.split(' ').slice(0, 2).map((w) => w[0]).join('').toUpperCase()
}

// Fired when an item arrives in a column (via cross-column drag)
async function onColChange(status, change) {
  if (change.added) {
    const app = change.added.element
    app.status = status
    await api.put(`/applications/${app.id}/status`, { status })
  }
}

function openInterviewModal(app) {
  selectedApp.value = app
  showModal.value = true
}
</script>

<template>
  <AppLayout>
    <div class="p-6">
      <!-- Page header -->
      <div class="mb-6">
        <h1 class="text-xl font-bold text-slate-900 dark:text-slate-100">Управление кандидатами</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Перетащите карточку для смены статуса</p>
      </div>

      <!-- Kanban board -->
      <div class="flex gap-4 overflow-x-auto pb-4">
        <div
          v-for="col in columns"
          :key="col.key"
          class="w-72 shrink-0 flex flex-col"
        >
          <!-- Column header -->
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <div :class="['w-2.5 h-2.5 rounded-full', col.dot]"></div>
              <span class="font-semibold text-slate-700 dark:text-slate-300 text-sm">{{ col.label }}</span>
            </div>
            <span :class="['text-xs rounded-full px-2 py-0.5 font-medium', col.badge]">
              {{ colApps[col.key].length }}
            </span>
          </div>

          <!-- Draggable column -->
          <VueDraggable
            v-model="colApps[col.key]"
            :group="{ name: 'kanban' }"
            :animation="200"
            @change="(e) => onColChange(col.key, e)"
            :class="[
              'min-h-32 rounded-xl border-2 border-t-4 p-2.5 space-y-2 flex-1',
              'bg-slate-100/60 dark:bg-slate-800/30 border-slate-200 dark:border-slate-700/50',
              col.top,
            ]"
          >
            <div
              v-for="app in colApps[col.key]"
              :key="app.id"
              class="bg-white dark:bg-[#1E2235] rounded-xl border border-slate-200 dark:border-slate-700/60 p-3.5 cursor-grab active:cursor-grabbing hover:shadow-md dark:hover:shadow-black/30 hover:-translate-y-0.5 transition-all"
            >
              <!-- Avatar + name -->
              <div class="flex items-start gap-2.5">
                <div class="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-950/70 flex items-center justify-center shrink-0">
                  <span class="text-indigo-600 dark:text-indigo-400 text-xs font-bold">
                    {{ initials(candidateForApp(app)?.full_name) }}
                  </span>
                </div>
                <div class="min-w-0">
                  <p class="font-semibold text-slate-800 dark:text-slate-200 text-sm leading-tight truncate">
                    {{ candidateForApp(app)?.full_name || 'Кандидат #' + app.candidate_id }}
                  </p>
                  <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5 truncate">
                    {{ candidateForApp(app)?.email }}
                  </p>
                </div>
              </div>

              <!-- Skills -->
              <div v-if="candidateForApp(app)?.skills" class="mt-2.5">
                <p class="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                  {{ candidateForApp(app)?.skills }}
                </p>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-2 mt-2.5 pt-2.5 border-t border-slate-100 dark:border-slate-700/50">
                <a
                  v-if="candidateForApp(app)?.resume_url"
                  :href="candidateForApp(app)?.resume_url"
                  target="_blank"
                  class="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
                >
                  📄 Резюме
                </a>
                <button
                  v-if="app.status === 'interview'"
                  @click="openInterviewModal(app)"
                  class="text-xs font-medium text-violet-600 dark:text-violet-400 hover:underline ml-auto"
                >
                  + Собеседование
                </button>
              </div>
            </div>
          </VueDraggable>
        </div>
      </div>
    </div>

    <InterviewModal
      v-if="showModal"
      :application="selectedApp"
      @close="showModal = false"
      @created="showModal = false; loadData()"
    />
  </AppLayout>
</template>
