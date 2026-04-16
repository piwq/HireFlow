import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

const STATUS_LABELS = {
  new: 'Новый', screening: 'На рассмотрении', interview: 'HR-интервью',
  manager_interview: 'Интервью с руководителем', interview_done: 'Интервью проведено',
  awaiting_decision: 'Ожидает решения', reserve: 'Резерв', offer: 'Получен оффер',
  hired: 'Принят на работу', rejected: 'Отказ', accepted: 'Принят',
}

function buildText(event, data) {
  switch (event) {
    case 'application_status':
      return `Статус заявки изменён: ${STATUS_LABELS[data.status] ?? data.status}`
    case 'interview_scheduled':
      return `Интервью назначено на ${new Date(data.scheduled_at).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}`
    case 'interview_assigned':
      return `Вам назначено интервью на ${new Date(data.scheduled_at).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}`
    case 'interview_request_new':
      return 'Новый запрос на интервью от руководителя'
    case 'interview_request_updated':
      return data.status === 'accepted'
        ? 'Ваш запрос на интервью принят'
        : 'Ваш запрос на интервью отклонён'
    default:
      return 'Новое уведомление'
  }
}

function buildIcon(event) {
  switch (event) {
    case 'application_status': return '📋'
    case 'interview_scheduled':
    case 'interview_assigned': return '📅'
    case 'interview_request_new': return '🔔'
    case 'interview_request_updated': return '✅'
    default: return '💬'
  }
}

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref([])

  const unreadCount = computed(() => items.value.filter(n => !n.read).length)

  function add(msg) {
    items.value.unshift({
      id: Date.now(),
      event: msg.event,
      data: msg.data,
      text: buildText(msg.event, msg.data ?? {}),
      icon: buildIcon(msg.event),
      read: false,
      at: new Date(),
    })
    if (items.value.length > 50) items.value.pop()
  }

  function markAllRead() {
    items.value.forEach(n => { n.read = true })
  }

  return { items, unreadCount, add, markAllRead }
})
