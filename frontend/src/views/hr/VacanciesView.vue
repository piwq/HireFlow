<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'
import {
  Briefcase,
  Plus,
  Trash2,
  Loader2,
  X,
  AlertCircle,
  Users,
} from 'lucide-vue-next'

const vacancies = ref([])
const appCountMap = ref({}) // vacancy_id → count
const loading = ref(true)
const showForm = ref(false)
const form = ref({ title: '', description: '' })
const saving = ref(false)
const error = ref('')

onMounted(loadVacancies)

async function loadVacancies() {
  loading.value = true
  try {
    const [vacRes, appsRes] = await Promise.all([
      api.get('/vacancies/'),
      api.get('/applications/'),
    ])
    vacancies.value = vacRes.data
    const counts = {}
    for (const app of appsRes.data) {
      counts[app.vacancy_id] = (counts[app.vacancy_id] || 0) + 1
    }
    appCountMap.value = counts
  } finally {
    loading.value = false
  }
}

async function createVacancy() {
  error.value = ''
  if (!form.value.title.trim()) {
    error.value = 'Название обязательно'
    return
  }
  saving.value = true
  try {
    const { data } = await api.post('/vacancies/', form.value)
    vacancies.value.unshift(data)
    form.value = { title: '', description: '' }
    showForm.value = false
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка создания'
  } finally {
    saving.value = false
  }
}

async function deleteVacancy(id) {
  try {
    await api.delete(`/vacancies/${id}`)
    vacancies.value = vacancies.value.filter(v => v.id !== id)
  } catch {}
}
</script>

<template>
  <div class="bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <!-- Header -->
    <div class="p-4 md:p-8 pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-display text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
          <Briefcase class="w-7 h-7 text-brand-accent" />
          Вакансии
        </h1>
        <p class="text-sm md:text-body text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Управляйте открытыми позициями компании</p>
      </div>
      <button
        @click="showForm = !showForm"
        class="flex items-center gap-2 px-4 py-2.5 bg-brand-accent hover:bg-brand-accent-hover text-white rounded-xl text-body font-bold transition-all shadow-lg shadow-brand-accent/25 active:scale-[0.98]"
      >
        <Plus class="w-4 h-4" />
        Новая вакансия
      </button>
    </div>

    <!-- Create form (inline) -->
    <div v-if="showForm" class="px-4 md:px-8 pb-4">
      <div class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl p-6 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Новая вакансия</h3>
          <button @click="showForm = false; error = ''" class="p-1.5 hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated rounded-lg text-brand-light-muted dark:text-brand-dark-muted transition-colors">
            <X class="w-4 h-4" />
          </button>
        </div>

        <div class="space-y-3">
          <input
            v-model="form.title"
            type="text"
            placeholder="Название вакансии"
            class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/10 transition-all"
          />
          <textarea
            v-model="form.description"
            rows="3"
            placeholder="Описание, требования, условия..."
            class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/10 transition-all resize-none"
          />
        </div>

        <div v-if="error" class="flex items-start gap-3 bg-red-500/5 border border-red-500/20 rounded-xl p-4">
          <AlertCircle class="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
          <p class="text-caption text-red-500">{{ error }}</p>
        </div>

        <div class="flex gap-3 pt-1">
          <button
            @click="showForm = false; error = ''"
            class="flex-1 py-3 border border-brand-light-border dark:border-brand-dark-border rounded-xl text-body font-bold text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated transition-all"
          >
            Отмена
          </button>
          <button
            @click="createVacancy"
            :disabled="saving"
            class="flex-2 py-3 bg-brand-accent hover:bg-brand-accent-hover disabled:opacity-60 text-white rounded-xl text-body font-bold transition-all shadow-lg shadow-brand-accent/25 flex items-center justify-center gap-2"
          >
            <Loader2 v-if="saving" class="w-4 h-4 animate-spin" />
            {{ saving ? 'Создание...' : 'Создать' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="p-4 md:p-8 pt-4">
      <div v-if="loading" class="flex items-center justify-center h-64">
        <Loader2 class="w-10 h-10 animate-spin text-brand-accent" />
      </div>

      <div v-else-if="vacancies.length === 0" class="flex flex-col items-center justify-center h-64 gap-4 text-center">
        <div class="w-16 h-16 rounded-2xl bg-brand-light-elevated dark:bg-brand-dark-elevated flex items-center justify-center">
          <Briefcase class="w-8 h-8 text-brand-light-muted dark:text-brand-dark-muted" />
        </div>
        <div>
          <p class="text-body font-semibold text-brand-light-primary dark:text-brand-dark-primary">Нет открытых вакансий</p>
          <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Создайте первую вакансию для привлечения кандидатов</p>
        </div>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="vacancy in vacancies"
          :key="vacancy.id"
          class="group bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl p-6 hover:shadow-xl hover:shadow-brand-accent/5 hover:-translate-y-1 transition-all duration-300"
        >
          <div class="flex items-start justify-between gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center shrink-0">
              <Briefcase class="w-5 h-5 text-brand-accent" />
            </div>
            <button
              @click="deleteVacancy(vacancy.id)"
              class="p-1.5 opacity-0 group-hover:opacity-100 hover:bg-red-500/10 hover:text-red-500 rounded-lg text-brand-light-muted dark:text-brand-dark-muted transition-all"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>

          <h3 class="text-heading text-brand-light-primary dark:text-brand-dark-primary mb-2">{{ vacancy.title }}</h3>
          <p v-if="vacancy.description" class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary line-clamp-3">
            {{ vacancy.description }}
          </p>
          <p v-else class="text-caption text-brand-light-muted dark:text-brand-dark-muted italic">Описание не добавлено</p>

          <div class="mt-5 pt-4 border-t border-brand-light-border dark:border-brand-dark-border flex items-center gap-2 text-caption text-brand-light-secondary dark:text-brand-dark-secondary">
            <Users class="w-3.5 h-3.5" />
            <span>{{ appCountMap[vacancy.id] || 0 }} {{ appCountMap[vacancy.id] === 1 ? 'отклик' : (appCountMap[vacancy.id] >= 2 && appCountMap[vacancy.id] <= 4) ? 'отклика' : 'откликов' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
