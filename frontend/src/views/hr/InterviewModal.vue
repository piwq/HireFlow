<script setup>
import { ref } from 'vue'
import api from '@/api/index.js'

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
    class="fixed inset-0 bg-black/50 dark:bg-black/70 flex items-center justify-center z-50 p-4"
    @click.self="emit('close')"
  >
    <div class="bg-white dark:bg-[#1E2235] rounded-2xl border border-slate-200 dark:border-[#2A2F4A] shadow-2xl p-6 w-full max-w-sm">
      <h2 class="text-lg font-bold text-slate-900 dark:text-slate-100 mb-5">Назначить собеседование</h2>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Дата</label>
          <input
            v-model="date"
            type="date"
            class="w-full bg-slate-50 dark:bg-[#151827] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Время</label>
          <input
            v-model="time"
            type="time"
            class="w-full bg-slate-50 dark:bg-[#151827] border border-slate-300 dark:border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition"
          />
        </div>
        <div v-if="error" class="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-lg px-3.5 py-2.5">
          <p class="text-red-600 dark:text-red-400 text-sm">{{ error }}</p>
        </div>
      </div>

      <div class="flex gap-2 mt-5">
        <button
          @click="emit('close')"
          class="flex-1 py-2.5 border border-slate-300 dark:border-slate-700 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition"
        >
          Отмена
        </button>
        <button
          @click="submit"
          :disabled="loading"
          class="flex-1 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-60 text-white text-sm font-semibold rounded-lg transition shadow-md shadow-violet-500/25"
        >
          {{ loading ? 'Создаю...' : 'Назначить' }}
        </button>
      </div>
    </div>
  </div>
</template>
