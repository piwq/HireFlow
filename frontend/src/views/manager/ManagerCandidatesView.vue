<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/index.js'
import { Users, Search, Loader2, Send, X } from 'lucide-vue-next'

// Data
const candidates = ref([])
const loading = ref(true)
const search = ref('')

// Interview request modal
const showModal = ref(false)
const selectedCandidate = ref(null)
const form = ref({ comment: '', preferred_format: '', preferred_time: '' })
const submitting = ref(false)
const submitted = ref({}) // { [candidate_id]: true }

onMounted(load)

async function load() {
  loading.value = true
  try {
    const res = await api.get('/candidates/')
    candidates.value = res.data
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  if (!search.value) return candidates.value
  const q = search.value.toLowerCase()
  return candidates.value.filter(c =>
    c.full_name?.toLowerCase().includes(q) ||
    c.email?.toLowerCase().includes(q) ||
    c.desired_position?.toLowerCase().includes(q) ||
    c.skills?.toLowerCase().includes(q)
  )
})

function openModal(candidate) {
  selectedCandidate.value = candidate
  form.value = { comment: '', preferred_format: 'online', preferred_time: '' }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedCandidate.value = null
}

async function submitRequest() {
  if (!selectedCandidate.value) return
  submitting.value = true
  try {
    await api.post('/interview-requests/', {
      candidate_id: selectedCandidate.value.id,
      comment: form.value.comment || null,
      preferred_format: form.value.preferred_format || null,
      preferred_time: form.value.preferred_time || null,
    })
    submitted.value[selectedCandidate.value.id] = true
    closeModal()
  } finally {
    submitting.value = false
  }
}

const FORMAT_OPTIONS = [
  { value: 'online', label: 'Онлайн' },
  { value: 'offline', label: 'Офлайн' },
  { value: 'phone', label: 'Телефон' },
]

const LEVEL_COLORS = {
  junior: 'bg-green-500/10 text-green-500',
  middle: 'bg-blue-500/10 text-blue-500',
  senior: 'bg-purple-500/10 text-purple-500',
  lead: 'bg-orange-500/10 text-orange-500',
}

function initials(name) {
  if (!name) return '?'
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}
</script>

<template>
  <div class="p-6 md:p-8">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div class="flex items-center gap-3">
          <Users class="w-7 h-7 text-brand-accent" />
          <div>
            <h1 class="text-2xl font-bold text-brand-light-primary dark:text-brand-dark-primary">Кандидаты</h1>
            <p class="text-sm text-brand-light-secondary dark:text-brand-dark-secondary mt-0.5">Просматривайте профили и запрашивайте встречи</p>
          </div>
        </div>
        <div class="relative w-full md:w-72">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-brand-light-muted dark:text-brand-dark-muted" />
          <input
            v-model="search"
            type="text"
            placeholder="Поиск по имени, должности..."
            class="w-full bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent transition-all"
          />
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-20">
        <Loader2 class="w-10 h-10 animate-spin text-brand-accent" />
      </div>

      <!-- Empty -->
      <div v-else-if="filtered.length === 0" class="text-center py-20 text-brand-light-secondary dark:text-brand-dark-secondary">
        Кандидаты не найдены
      </div>

      <!-- Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="c in filtered"
          :key="c.id"
          class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl p-5 flex flex-col gap-4"
        >
          <!-- Top row -->
          <div class="flex items-start gap-3">
            <div class="w-11 h-11 rounded-xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center shrink-0">
              <span class="text-brand-accent font-bold text-sm">{{ initials(c.full_name) }}</span>
            </div>
            <div class="min-w-0 flex-1">
              <h3 class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-sm truncate">
                {{ c.full_name || 'Без имени' }}
              </h3>
              <p class="text-xs text-brand-light-secondary dark:text-brand-dark-secondary truncate mt-0.5">
                {{ c.desired_position || c.email }}
              </p>
            </div>
          </div>

          <!-- Badges -->
          <div class="flex flex-wrap gap-1.5">
            <span v-if="c.level" :class="['text-xs px-2 py-0.5 rounded-md font-medium', LEVEL_COLORS[c.level] || 'bg-gray-400/10 text-gray-400']">
              {{ c.level }}
            </span>
            <span v-if="c.city" class="text-xs px-2 py-0.5 rounded-md bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary border border-brand-light-border dark:border-brand-dark-border">
              {{ c.city }}
            </span>
            <span v-if="c.salary_from" class="text-xs px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
              от {{ c.salary_from.toLocaleString('ru-RU') }} ₽
            </span>
          </div>

          <!-- Skills -->
          <div v-if="c.skills" class="flex flex-wrap gap-1">
            <span
              v-for="skill in c.skills.split(',').slice(0, 4)"
              :key="skill"
              class="text-xs px-1.5 py-0.5 rounded bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary"
            >
              {{ skill.trim() }}
            </span>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 mt-auto pt-2 border-t border-brand-light-border dark:border-brand-dark-border">
            <button
              @click="openModal(c)"
              :class="[
                'flex-1 flex items-center justify-center gap-1.5 py-2 rounded-xl text-sm font-medium transition-colors',
                submitted[c.id]
                  ? 'bg-green-500/10 text-green-500 border border-green-500/20 cursor-default'
                  : 'bg-brand-accent text-white hover:bg-brand-accent-hover'
              ]"
              :disabled="submitted[c.id]"
            >
              <Send class="w-3.5 h-3.5" />
              {{ submitted[c.id] ? 'Запрос отправлен' : 'Запросить интервью' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: request interview -->
    <Teleport to="body">
      <div
        v-if="showModal"
        class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        @click.self="closeModal"
      >
        <div class="bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl p-6 w-full max-w-md shadow-2xl">
          <div class="flex items-center justify-between mb-5">
            <h2 class="text-lg font-bold text-brand-light-primary dark:text-brand-dark-primary">
              Запрос интервью
            </h2>
            <button @click="closeModal" class="p-1 rounded-lg hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated text-brand-light-muted dark:text-brand-dark-muted">
              <X class="w-5 h-5" />
            </button>
          </div>

          <p class="text-sm text-brand-light-secondary dark:text-brand-dark-secondary mb-5">
            Кандидат: <strong class="text-brand-light-primary dark:text-brand-dark-primary">{{ selectedCandidate?.full_name }}</strong>
          </p>

          <div class="space-y-4">
            <!-- Format -->
            <div>
              <label class="block text-xs font-semibold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-2">Формат</label>
              <div class="flex gap-2">
                <button
                  v-for="opt in FORMAT_OPTIONS"
                  :key="opt.value"
                  @click="form.preferred_format = opt.value"
                  :class="[
                    'flex-1 py-2 rounded-xl text-sm font-medium border transition-all',
                    form.preferred_format === opt.value
                      ? 'bg-brand-accent text-white border-brand-accent'
                      : 'bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary border-brand-light-border dark:border-brand-dark-border hover:border-brand-accent/40'
                  ]"
                >
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- Time -->
            <div>
              <label class="block text-xs font-semibold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-2">Желаемое время</label>
              <input
                v-model="form.preferred_time"
                type="text"
                placeholder="Например: вторник–четверг, 10:00–18:00"
                class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2.5 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent transition-all"
              />
            </div>

            <!-- Comment -->
            <div>
              <label class="block text-xs font-semibold text-brand-light-secondary dark:text-brand-dark-secondary uppercase tracking-wider mb-2">Комментарий</label>
              <textarea
                v-model="form.comment"
                rows="3"
                placeholder="Что именно хотите обсудить на встрече?"
                class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-2.5 text-sm text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-accent transition-all resize-none"
              ></textarea>
            </div>
          </div>

          <div class="flex gap-3 mt-6">
            <button
              @click="closeModal"
              class="flex-1 py-2.5 rounded-xl text-sm font-medium text-brand-light-secondary dark:text-brand-dark-secondary bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border hover:bg-brand-light-border dark:hover:bg-brand-dark-border transition-colors"
            >
              Отмена
            </button>
            <button
              @click="submitRequest"
              :disabled="submitting"
              class="flex-1 py-2.5 rounded-xl text-sm font-bold text-white bg-brand-accent hover:bg-brand-accent-hover transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
              <Send v-else class="w-4 h-4" />
              Отправить запрос
            </button>
          </div>
        </div>
      </div>
    </Teleport>
</template>
