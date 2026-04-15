<script setup>
import { ref } from 'vue'
import api from '@/api/index.js'
import { Calendar, Clock, X, Loader2, AlertCircle } from 'lucide-vue-next'

const props = defineProps({ application: Object })
const emit = defineEmits(['close', 'created'])

const date = ref('')
const time = ref('')
const error = ref('')
const loading = ref(false)

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
          <h2 class="text-heading text-brand-light-primary dark:text-brand-dark-primary">Собеседование</h2>
        </div>
        <button @click="emit('close')" class="p-2 hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated rounded-xl transition-colors text-brand-light-muted">
          <X class="w-5 h-5" />
        </button>
      </div>

      <div class="space-y-6">
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

        <div v-if="error" class="flex items-start gap-3 bg-red-500/5 border border-red-500/20 rounded-xl p-4">
          <AlertCircle class="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <p class="text-caption text-red-500">{{ error }}</p>
        </div>
      </div>

      <div class="flex gap-3 mt-10">
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
