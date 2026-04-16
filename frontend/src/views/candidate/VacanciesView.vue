<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api/index.js'
import { 
  Briefcase, 
  Search, 
  MapPin, 
  Clock, 
  DollarSign, 
  CheckCircle, 
  Send,
  Loader2,
  X,
  FileText
} from 'lucide-vue-next'

const vacancies = ref([])
const myApplications = ref([])
const loading = ref(true)
const search = ref('')
const applying = ref(null) // ID of vacancy being applied to
const showSuccessModal = ref(false)

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const [vacRes, appRes] = await Promise.all([
      api.get('/vacancies/'),
      api.get('/applications/my')
    ])
    vacancies.value = vacRes.data
    myApplications.value = appRes.data
  } catch (e) {
    console.error('Failed to load data', e)
  } finally {
    loading.value = false
  }
}

const filteredVacancies = computed(() => {
  if (!search.value) return vacancies.value
  const q = search.value.toLowerCase()
  return vacancies.value.filter(v => 
    v.title.toLowerCase().includes(q) || 
    v.description?.toLowerCase().includes(q)
  )
})

function hasApplied(vacancyId) {
  return myApplications.value.some(a => a.vacancy_id === vacancyId)
}

async function apply(vacancyId) {
  applying.value = vacancyId
  try {
    await api.post('/applications/', { vacancy_id: vacancyId })
    // Refresh apps
    const res = await api.get('/applications/my')
    myApplications.value = res.data
    showSuccessModal.value = true
    setTimeout(() => { showSuccessModal.value = false }, 3000)
  } catch (e) {
    if (e.response?.data?.detail === "Complete your profile first") {
      alert("Пожалуйста, сначала заполните профиль для отклика на вакансию.")
    } else {
      alert(e.response?.data?.detail || "Ошибка при отклике")
    }
  } finally {
    applying.value = null
  }
}

// Utility to extract "salary" or other badges from description if it was structured
// For now we just show a placeholder since our Vacancy model is simple
</script>

<template>
  <div class="h-full flex flex-col bg-brand-light-base dark:bg-brand-dark-base antialiased">
    <!-- Header -->
    <div class="p-6 md:p-8 pb-4">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl md:text-3xl font-bold text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-3">
            <Briefcase class="w-8 h-8 text-brand-accent" />
            Доступные вакансии
          </h1>
          <p class="text-sm md:text-base text-brand-light-secondary dark:text-brand-dark-secondary mt-1">
            Найдите работу своей мечты в нашей компании
          </p>
        </div>
        
        <div class="relative w-full md:w-80">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted" />
          <input
            v-model="search"
            type="text"
            placeholder="Поиск по названию или описанию..."
            class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent transition-all shadow-sm"
          />
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 p-6 md:p-8 pt-2 overflow-y-auto">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <Loader2 class="w-10 h-10 animate-spin text-brand-accent" />
      </div>

      <div v-else-if="filteredVacancies.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
        <div class="w-20 h-20 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-full flex items-center justify-center mb-4">
          <Briefcase class="w-10 h-10 text-brand-light-muted dark:text-brand-dark-muted" />
        </div>
        <h3 class="text-lg font-bold text-brand-light-primary dark:text-brand-dark-primary">Вакансии не найдены</h3>
        <p class="text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Попробуйте изменить параметры поиска</p>
      </div>

      <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div 
          v-for="v in filteredVacancies" 
          :key="v.id"
          class="group bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl p-6 transition-all duration-300 hover:shadow-xl hover:shadow-brand-accent/5 hover:border-brand-accent/30 flex flex-col"
        >
          <div class="flex justify-between items-start gap-4 mb-4">
            <div class="flex-1">
              <h2 class="text-xl font-bold text-brand-light-primary dark:text-brand-dark-primary group-hover:text-brand-accent transition-colors">
                {{ v.title }}
              </h2>
              <div class="flex flex-wrap gap-4 mt-2 text-sm text-brand-light-secondary dark:text-brand-dark-secondary">
                <span class="flex items-center gap-1.5"><MapPin class="w-3.5 h-3.5" /> Гибрид / Офис</span>
                <span class="flex items-center gap-1.5"><Clock class="w-3.5 h-3.5" /> Полная занятость</span>
                <span class="flex items-center gap-1.5 text-emerald-500 font-medium"><DollarSign class="w-3.5 h-3.5" /> З/П обсуждается</span>
              </div>
            </div>
            <div v-if="hasApplied(v.id)" class="px-3 py-1.5 bg-green-500/10 text-green-500 rounded-lg text-xs font-bold flex items-center gap-1.5 border border-green-500/20">
              <CheckCircle class="w-3.5 h-3.5" /> Вы откликнулись
            </div>
          </div>

          <div class="flex-1 border-t border-brand-light-border dark:border-brand-dark-border pt-4 mt-auto">
            <h3 class="text-xs font-bold text-brand-light-muted dark:text-brand-dark-muted uppercase tracking-wider mb-2">Описание</h3>
            <p class="text-sm text-brand-light-secondary dark:text-brand-dark-secondary line-clamp-3">
              {{ v.description || 'Детальное описание вакансии будет предоставлено на собеседовании.' }}
            </p>
          </div>

          <div class="mt-6 flex gap-3">
            <button 
              @click="apply(v.id)"
              :disabled="hasApplied(v.id) || applying === v.id"
              class="flex-1 py-3 rounded-xl text-sm font-bold transition-all flex items-center justify-center gap-2 shadow-lg active:scale-[0.98] disabled:active:scale-100 disabled:opacity-70 disabled:cursor-not-allowed"
              :class="hasApplied(v.id) 
                ? 'bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-muted dark:text-brand-dark-muted shadow-none border border-brand-light-border dark:border-brand-dark-border' 
                : 'bg-brand-accent hover:bg-brand-accent-hover text-white shadow-brand-accent/20'"
            >
              <Loader2 v-if="applying === v.id" class="w-4 h-4 animate-spin" />
              <Send v-else-if="!hasApplied(v.id)" class="w-4 h-4" />
              <CheckCircle v-else class="w-4 h-4 text-green-500" />
              {{ hasApplied(v.id) ? 'Отклик отправлен' : (applying === v.id ? 'Отправка...' : 'Откликнуться') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Feedback Overlay -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-300 pointer-events-none"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 pointer-events-none"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-4"
      >
        <div v-if="showSuccessModal" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-50">
          <div class="bg-emerald-500 text-white px-6 py-4 rounded-2xl shadow-xl shadow-emerald-500/20 flex items-center gap-3">
            <CheckCircle class="w-6 h-6" />
            <div>
              <p class="font-bold">Успешно откликнулись!</p>
              <p class="text-xs opacity-90">Ваша заявка передана HR-менеджеру</p>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
