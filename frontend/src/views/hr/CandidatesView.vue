<script setup>
import { ref, onMounted, computed } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import { useAuthStore } from '@/stores/auth.js'
import api from '@/api/index.js'
import InterviewModal from './InterviewModal.vue'

const auth = useAuthStore()

const columns = [
  { key: 'new', label: 'Новые' },
  { key: 'screening', label: 'Скрининг' },
  { key: 'interview', label: 'Интервью' },
  { key: 'hired', label: 'Нанят' },
  { key: 'rejected', label: 'Отказ' },
]

const columnColors = {
  new: 'bg-blue-50 border-blue-200',
  screening: 'bg-yellow-50 border-yellow-200',
  interview: 'bg-purple-50 border-purple-200',
  hired: 'bg-green-50 border-green-200',
  rejected: 'bg-red-50 border-red-200',
}

const applications = ref([])
const candidates = ref([])
const showModal = ref(false)
const selectedApp = ref(null)

onMounted(async () => {
  await loadData()
})

async function loadData() {
  const [appsRes, candidatesRes] = await Promise.all([
    api.get('/applications/'),
    api.get('/candidates/'),
  ])
  applications.value = appsRes.data
  candidates.value = candidatesRes.data
}

function candidateForApp(app) {
  return candidates.value.find((c) => c.id === app.candidate_id)
}

function appsByStatus(status) {
  return applications.value.filter((a) => a.status === status)
}

async function onDragEnd(status, items) {
  // items after drag = new order in this column — just update the moved item
  // VueDraggable gives us the new array; find which item changed status
  for (const app of items) {
    if (app.status !== status) {
      await api.put(`/applications/${app.id}/status`, { status })
      app.status = status
    }
  }
}

function openInterviewModal(app) {
  selectedApp.value = app
  showModal.value = true
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <div class="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
      <h1 class="text-xl font-bold text-gray-800">HR — Управление кандидатами</h1>
      <button @click="auth.logout(); $router.push('/login')" class="text-sm text-gray-500 hover:text-red-500">
        Выйти
      </button>
    </div>

    <!-- Kanban board -->
    <div class="p-6 overflow-x-auto">
      <div class="flex gap-4 min-w-max">
        <div
          v-for="col in columns"
          :key="col.key"
          class="w-72 flex flex-col"
        >
          <!-- Column header -->
          <div class="flex items-center justify-between mb-2">
            <span class="font-semibold text-gray-700 text-sm uppercase tracking-wide">{{ col.label }}</span>
            <span class="text-xs bg-gray-200 text-gray-600 rounded-full px-2 py-0.5">
              {{ appsByStatus(col.key).length }}
            </span>
          </div>

          <!-- Draggable column -->
          <VueDraggable
            :model-value="appsByStatus(col.key)"
            @update:model-value="(items) => onDragEnd(col.key, items)"
            group="kanban"
            :class="['min-h-32 rounded-xl border-2 p-2 space-y-2 flex-1', columnColors[col.key]]"
            item-key="id"
          >
            <template #item="{ element: app }">
              <div class="bg-white rounded-lg shadow-sm p-3 cursor-grab active:cursor-grabbing">
                <div class="font-medium text-gray-800 text-sm">
                  {{ candidateForApp(app)?.full_name || 'Кандидат #' + app.candidate_id }}
                </div>
                <div class="text-xs text-gray-500 mt-0.5">
                  {{ candidateForApp(app)?.email }}
                </div>
                <div v-if="candidateForApp(app)?.skills" class="text-xs text-gray-400 mt-1 line-clamp-2">
                  {{ candidateForApp(app)?.skills }}
                </div>
                <div class="flex gap-2 mt-2">
                  <a
                    v-if="candidateForApp(app)?.resume_url"
                    :href="candidateForApp(app)?.resume_url"
                    target="_blank"
                    class="text-xs text-blue-500 hover:underline"
                  >Резюме</a>
                  <button
                    v-if="app.status === 'interview'"
                    @click="openInterviewModal(app)"
                    class="text-xs text-purple-600 hover:underline"
                  >
                    + Собеседование
                  </button>
                </div>
              </div>
            </template>
          </VueDraggable>
        </div>
      </div>
    </div>

    <InterviewModal
      v-if="showModal"
      :application="selectedApp"
      @close="showModal = false"
      @created="showModal = false"
    />
  </div>
</template>
