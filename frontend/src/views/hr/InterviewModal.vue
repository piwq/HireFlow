<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/index.js'
import { Calendar, Clock, X, Loader2, AlertCircle, MapPin, MessageSquare, User } from 'lucide-vue-next'

const props = defineProps({ application: Object })
const emit = defineEmits(['close', 'created'])

const date = ref('')
const time = ref('')
const format = ref('online')
const location = ref('')
const comment = ref('')
const managerId = ref(null)
const managers = ref([])
const error = ref('')
const loading = ref(false)

onMounted(async () => {
  try {
    const { data } = await api.get('/users/')
    managers.value = data.filter(u => u.role === 'manager')
  } catch {}
})

async function submit() {
  error.value = ''
  if (!date.value || !time.value) {
    error.value = 'Выберите дату и время'
    return
  }
  loading.value = true
  try {
    await api.post('/interviews/', {
      application_id: props.application.id,
      scheduled_at: `${date.value}T${time.value}:00`,
      format: format.value,
      location: location.value || null,
      comment: comment.value || null,
      manager_id: managerId.value || null,
    })
    emit('created')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка создания'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="fixed inset-0 bg-brand-dark-base/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 transition-all duration-300"
    @click.self="emit('close')"
  >
    <div class="bg-brand-light-surface dark:bg-brand-dark-surface rounded-3xl border border-brand-light-border dark:border-brand-dark-border shadow-2xl shadow-brand-accent/20 p-8 w-full max-w-md transform transition-all scale-100 animate-in fade-in zoom-in-95 duration-200">
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-brand-status-interview/10 flex items-center justify-center">
            <Calendar class="w-5 h-5 text-brand-status-interview" />
          </div>
          <h2 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Назначить собеседование</h2>
        </div>
        <button @click="emit('close')" class="p-2 hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated rounded-xl transition-colors text-brand-light-muted">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div class="space-y-5">
        <!-- Date -->
        <div class="space-y-2">
          <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Дата встречи</label>
          <div class="relative group">
            <Calendar class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted group-focus-within:text-brand-status-interview transition-colors" />
            <input
              v-model="date"
              type="date"
              class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-11 pr-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-status-interview transition-all"
            />
          </div>
        </div>

        <!-- Time -->
        <div class="space-y-2">
          <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Время (МСК)</label>
          <div class="relative group">
            <Clock class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted group-focus-within:text-brand-status-interview transition-colors" />
            <input
              v-model="time"
              type="time"
              class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-11 pr-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-status-interview transition-all"
            />
          </div>
        </div>

        <!-- Format -->
        <div class="space-y-2">
          <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Формат</label>
          <div class="flex gap-2">
            <button
              v-for="f in [{v:'online',l:'Онлайн'},{v:'offline',l:'Офлайн'},{v:'phone',l:'Телефон'}]"
              :key="f.v"
              @click="format = f.v"
              :class="[
                'flex-1 py-2 rounded-xl text-sm font-bold transition-all border',
                format === f.v
                  ? 'bg-brand-status-interview text-white border-brand-status-interview shadow-lg shadow-brand-status-interview/20'
                  : 'bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary border-brand-light-border dark:border-brand-dark-border hover:border-brand-status-interview/50'
              ]"
            >
              {{ f.l }}
            </button>
          </div>
        </div>

        <!-- Location / Link -->
        <div class="space-y-2">
          <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">
            {{ format === 'online' ? 'Ссылка на встречу' : format === 'offline' ? 'Адрес' : 'Телефон' }}
          </label>
          <div class="relative">
            <MapPin class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted" />
            <input
              v-model="location"
              type="text"
              :placeholder="format === 'online' ? 'https://meet.google.com/...' : format === 'offline' ? 'Москва, ул. Пушкина, 10' : '+7 999 000-00-00'"
              class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-11 pr-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-status-interview transition-all"
            />
          </div>
        </div>

        <!-- Comment -->
        <div class="space-y-2">
          <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Комментарий</label>
          <div class="relative">
            <MessageSquare class="absolute left-3.5 top-3.5 w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted" />
            <textarea
              v-model="comment"
              rows="2"
              placeholder="Дополнительная информация для кандидата..."
              class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-11 pr-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-status-interview transition-all resize-none"
            />
          </div>
        </div>

        <!-- Manager -->
        <div v-if="managers.length > 0" class="space-y-2">
          <label class="text-label text-brand-light-primary dark:text-brand-dark-primary ml-1">Менеджер (необязательно)</label>
          <div class="relative">
            <User class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted" />
            <select
              v-model="managerId"
              class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl pl-11 pr-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary focus:outline-none focus:border-brand-status-interview transition-all appearance-none"
            >
              <option :value="null">— Не назначать —</option>
              <option v-for="m in managers" :key="m.id" :value="m.id">
                {{ m.full_name || m.email }}
              </option>
            </select>
          </div>
        </div>

        <div v-if="error" class="flex items-start gap-3 bg-red-500/5 border border-red-500/20 rounded-xl p-4">
          <AlertCircle class="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <p class="text-caption text-red-500">{{ error }}</p>
        </div>
      </div>

      <div class="flex gap-3 mt-8">
        <button
          @click="emit('close')"
          class="flex-1 py-3.5 border border-brand-light-border dark:border-brand-dark-border rounded-xl text-body font-bold text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated transition-all"
        >
          Отмена
        </button>
        <button
          @click="submit"
          :disabled="loading"
          class="flex-2 py-3.5 bg-brand-status-interview hover:opacity-90 disabled:opacity-60 text-white text-body font-bold rounded-xl transition-all shadow-lg shadow-brand-status-interview/25 flex items-center justify-center gap-2"
        >
          <Loader2 v-if="loading" class="w-5 h-5 animate-spin" />
          {{ loading ? 'Создание...' : 'Назначить' }}
        </button>
      </div>
    </div>
  </div>
</template>
