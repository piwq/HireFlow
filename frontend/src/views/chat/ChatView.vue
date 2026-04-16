<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import api from '@/api/index.js'
import {
  MessageSquare,
  Send,
  Search,
  Loader2,
  Users,
  User,
  Briefcase,
  Calendar,
  Wifi,
  WifiOff,
} from 'lucide-vue-next'

const currentUserId = parseInt(localStorage.getItem('user_id'))

const users = ref([])
const selectedUser = ref(null)
const messages = ref([])
const newMessage = ref('')
const search = ref('')
const ws = ref(null)
const connected = ref(false)
const loadingMessages = ref(false)
const messagesEnd = ref(null)

const ROLE_LABEL = { candidate: 'Кандидат', hr: 'HR', manager: 'Менеджер' }
const ROLE_COLOR = {
  candidate: 'text-brand-status-new',
  hr: 'text-brand-accent',
  manager: 'text-brand-status-interview',
}

const filteredUsers = computed(() => {
  const q = search.value.toLowerCase()
  if (!q) return users.value
  return users.value.filter(u => {
    const name = (u.full_name || u.email).toLowerCase()
    return name.includes(q) || u.role.includes(q)
  })
})

onMounted(async () => {
  await loadUsers()
  connectWS()
})

onUnmounted(() => {
  ws.value?.close()
})

async function loadUsers() {
  try {
    const { data } = await api.get('/users/')
    users.value = data
  } catch {}
}

async function selectUser(user) {
  selectedUser.value = user
  loadingMessages.value = true
  try {
    const { data } = await api.get(`/messages/${user.id}`)
    messages.value = data
  } catch {
    messages.value = []
  } finally {
    loadingMessages.value = false
    scrollToBottom()
  }
}

function connectWS() {
  const token = localStorage.getItem('token')
  if (!token) return
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const url = `${protocol}//${window.location.host}/api/ws?token=${token}`

  const socket = new WebSocket(url)

  socket.onopen = () => {
    connected.value = true
    ws.value = socket
  }

  socket.onmessage = (event) => {
    const msg = JSON.parse(event.data)
    if (!selectedUser.value) return
    const otherId = selectedUser.value.id
    if (msg.sender_id === otherId || msg.receiver_id === otherId) {
      // avoid duplicate if we already added it optimistically
      if (!messages.value.find(m => m.id === msg.id)) {
        messages.value.push(msg)
        scrollToBottom()
      }
    }
  }

  socket.onclose = () => {
    connected.value = false
    ws.value = null
    // Reconnect after 3s
    setTimeout(connectWS, 3000)
  }

  socket.onerror = () => {
    socket.close()
  }
}

function sendMessage() {
  const text = newMessage.value.trim()
  if (!text || !selectedUser.value) return

  if (ws.value?.readyState === WebSocket.OPEN) {
    ws.value.send(JSON.stringify({
      receiver_id: selectedUser.value.id,
      text,
    }))
    newMessage.value = ''
  }
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

function scrollToBottom() {
  nextTick(() => {
    messagesEnd.value?.scrollIntoView({ behavior: 'smooth' })
  })
}

function formatTime(dt) {
  return new Date(dt).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(dt) {
  const d = new Date(dt)
  const today = new Date()
  if (d.toDateString() === today.toDateString()) return 'Сегодня'
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  if (d.toDateString() === yesterday.toDateString()) return 'Вчера'
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

function displayName(user) {
  return user.full_name || user.email
}

function initials(user) {
  const name = user.full_name || user.email
  return name.split(/[\s@]/).slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

// Group messages by date for date separators
const groupedMessages = computed(() => {
  const groups = []
  let lastDate = null
  for (const msg of messages.value) {
    const date = formatDate(msg.created_at)
    if (date !== lastDate) {
      groups.push({ type: 'date', label: date })
      lastDate = date
    }
    groups.push({ type: 'msg', msg })
  }
  return groups
})
</script>

<template>
  <div class="bg-brand-light-base dark:bg-brand-dark-base antialiased flex h-full">
    <!-- User list panel -->
    <div class="w-72 shrink-0 flex flex-col border-r border-brand-light-border dark:border-brand-dark-border bg-brand-light-surface dark:bg-brand-dark-surface">
      <!-- Header -->
      <div class="p-4 border-b border-brand-light-border dark:border-brand-dark-border">
        <h2 class="text-heading text-brand-light-primary dark:text-brand-dark-primary flex items-center gap-2 mb-3">
          <MessageSquare class="w-5 h-5 text-brand-accent" />
          Чат
          <span class="ml-auto flex items-center gap-1.5 text-caption">
            <span :class="connected ? 'text-brand-status-hired' : 'text-brand-light-muted dark:text-brand-dark-muted'">
              <component :is="connected ? Wifi : WifiOff" class="w-3.5 h-3.5" />
            </span>
          </span>
        </h2>
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-brand-light-muted dark:text-brand-dark-muted" />
          <input
            v-model="search"
            type="text"
            placeholder="Поиск..."
            class="w-full bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-lg pl-9 pr-3 py-2 text-caption text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent transition-all"
          />
        </div>
      </div>

      <!-- User list -->
      <div class="flex-1 overflow-y-auto custom-scrollbar">
        <div v-if="users.length === 0" class="flex flex-col items-center justify-center h-32 text-center px-4">
          <Users class="w-8 h-8 text-brand-light-muted dark:text-brand-dark-muted mb-2" />
          <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Нет пользователей</p>
        </div>

        <button
          v-for="user in filteredUsers"
          :key="user.id"
          @click="selectUser(user)"
          class="w-full flex items-center gap-3 px-4 py-3 hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated transition-colors text-left border-b border-brand-light-border/50 dark:border-brand-dark-border/50"
          :class="selectedUser?.id === user.id ? 'bg-brand-accent/10 border-l-2 border-l-brand-accent' : ''"
        >
          <div class="w-9 h-9 rounded-xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center shrink-0 text-brand-accent text-xs font-bold">
            {{ initials(user) }}
          </div>
          <div class="min-w-0 flex-1">
            <p class="font-semibold text-brand-light-primary dark:text-brand-dark-primary text-sm truncate">
              {{ displayName(user) }}
            </p>
            <p class="text-micro truncate" :class="ROLE_COLOR[user.role]">
              {{ ROLE_LABEL[user.role] || user.role }}
            </p>
          </div>
        </button>
      </div>
    </div>

    <!-- Conversation panel -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Empty state -->
      <div v-if="!selectedUser" class="flex-1 flex flex-col items-center justify-center gap-4 text-center px-8">
        <div class="w-20 h-20 rounded-3xl bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border flex items-center justify-center">
          <MessageSquare class="w-10 h-10 text-brand-light-muted dark:text-brand-dark-muted" />
        </div>
        <div>
          <p class="text-body font-semibold text-brand-light-primary dark:text-brand-dark-primary">Выберите диалог</p>
          <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary mt-1">Нажмите на пользователя слева, чтобы начать переписку</p>
        </div>
      </div>

      <template v-else>
        <!-- Chat header -->
        <div class="px-6 py-4 border-b border-brand-light-border dark:border-brand-dark-border bg-brand-light-surface dark:bg-brand-dark-surface flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center text-brand-accent text-xs font-bold shrink-0">
            {{ initials(selectedUser) }}
          </div>
          <div>
            <p class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-sm">{{ displayName(selectedUser) }}</p>
            <p class="text-micro" :class="ROLE_COLOR[selectedUser.role]">{{ ROLE_LABEL[selectedUser.role] }}</p>
          </div>
        </div>

        <!-- Messages area -->
        <div class="flex-1 overflow-y-auto px-6 py-4 space-y-1 custom-scrollbar">
          <div v-if="loadingMessages" class="flex items-center justify-center h-32">
            <Loader2 class="w-8 h-8 animate-spin text-brand-accent" />
          </div>

          <template v-else>
            <template v-for="item in groupedMessages" :key="item.type === 'date' ? item.label : item.msg.id">
              <!-- Date separator -->
              <div v-if="item.type === 'date'" class="flex items-center gap-3 py-3">
                <div class="flex-1 h-px bg-brand-light-border dark:bg-brand-dark-border"></div>
                <span class="text-micro text-brand-light-muted dark:text-brand-dark-muted px-2">{{ item.label }}</span>
                <div class="flex-1 h-px bg-brand-light-border dark:bg-brand-dark-border"></div>
              </div>

              <!-- Message bubble -->
              <div
                v-else
                class="flex"
                :class="item.msg.sender_id === currentUserId ? 'justify-end' : 'justify-start'"
              >
                <div
                  class="max-w-xs lg:max-w-md px-4 py-2.5 rounded-2xl text-sm leading-relaxed"
                  :class="item.msg.sender_id === currentUserId
                    ? 'bg-brand-accent text-white rounded-br-sm'
                    : 'bg-brand-light-surface dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border text-brand-light-primary dark:text-brand-dark-primary rounded-bl-sm'"
                >
                  <p class="whitespace-pre-wrap break-words">{{ item.msg.text }}</p>
                  <p
                    class="text-micro mt-1 text-right"
                    :class="item.msg.sender_id === currentUserId ? 'text-white/60' : 'text-brand-light-muted dark:text-brand-dark-muted'"
                  >
                    {{ formatTime(item.msg.created_at) }}
                  </p>
                </div>
              </div>
            </template>

            <!-- Empty conversation -->
            <div v-if="groupedMessages.length === 0" class="flex flex-col items-center justify-center h-32 gap-2 text-center">
              <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Начните переписку с {{ displayName(selectedUser) }}</p>
            </div>

            <div ref="messagesEnd" />
          </template>
        </div>

        <!-- Input area -->
        <div class="px-4 py-4 border-t border-brand-light-border dark:border-brand-dark-border bg-brand-light-surface dark:bg-brand-dark-surface">
          <div class="flex items-end gap-3">
            <textarea
              v-model="newMessage"
              @keydown="onKeydown"
              rows="1"
              placeholder="Напишите сообщение..."
              class="flex-1 bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border rounded-xl px-4 py-3 text-body text-brand-light-primary dark:text-brand-dark-primary placeholder-brand-light-muted dark:placeholder-brand-dark-muted focus:outline-none focus:border-brand-accent focus:ring-4 focus:ring-brand-accent/10 transition-all resize-none max-h-32"
              style="field-sizing: content"
            />
            <button
              @click="sendMessage"
              :disabled="!newMessage.trim() || !connected"
              class="w-11 h-11 rounded-xl bg-brand-accent hover:bg-brand-accent-hover disabled:opacity-40 text-white flex items-center justify-center transition-all shadow-lg shadow-brand-accent/25 active:scale-95 shrink-0"
            >
              <Send class="w-4.5 h-4.5" />
            </button>
          </div>
          <p v-if="!connected" class="text-micro text-brand-light-muted dark:text-brand-dark-muted mt-2 flex items-center gap-1">
            <WifiOff class="w-3 h-3" />
            Переподключение...
          </p>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #2a2f4a; border-radius: 10px; }
</style>
