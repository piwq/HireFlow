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
  <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="emit('close')">
    <div class="bg-white rounded-2xl shadow-xl p-6 w-full max-w-sm">
      <h2 class="text-lg font-bold text-gray-800 mb-4">Назначить собеседование</h2>

      <div class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Дата</label>
          <input v-model="date" type="date"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Время</label>
          <input v-model="time" type="time"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500" />
        </div>
        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
      </div>

      <div class="flex gap-2 mt-5">
        <button @click="emit('close')"
          class="flex-1 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition text-sm">
          Отмена
        </button>
        <button @click="submit" :disabled="loading"
          class="flex-1 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition text-sm">
          {{ loading ? 'Создаю...' : 'Назначить' }}
        </button>
      </div>
    </div>
  </div>
</template>
