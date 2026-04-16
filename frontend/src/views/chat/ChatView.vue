<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/index.js'
import { unreadCounts, loadUnreadCounts, clearForUser, incrementForUser } from '@/stores/unread.js'
import { sendWS, setChatCallback, clearChatCallback, wsConnected } from '@/stores/ws.js'
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
const route = useRoute()

const users = ref([])
const selectedUser = ref(null)
const messages = ref([])
const newMessage = ref('')
const search = ref('')
const connected = wsConnected
const loadingMessages = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)
const offset = ref(0)
const limit = 50
const messagesEnd = ref(null)

const ROLE_LABEL = { candidate: 'Кандидат', hr: 'HR', manager: 'Менеджер' }
const ROLE_COLOR = {
  candidate: 'text-brand-status-new',
  hr: 'text-brand-accent',
  manager: 'text-brand-status-interview',
}

const filteredUsers = computed(() => {
  const q = search.value.toLowerCase()
  let list = users.value
  if (q) {
    list = list.filter(u => {
      const name = (u.full_name || u.email).toLowerCase()
      return name.includes(q) || u.role.includes(q)
    })
  }
  // Sort by last_message_at desc
  return [...list].sort((a, b) => {
    const tA = a.last_message_at ? new Date(a.last_message_at).getTime() : 0
    const tB = b.last_message_at ? new Date(b.last_message_at).getTime() : 0
    return tB - tA
  })
})

onMounted(async () => {
  await Promise.all([loadUsers(), loadUnreadCounts()])
  setChatCallback(handleChatMessage)
  const targetUserId = route.query.user ? parseInt(route.query.user) : null
  if (targetUserId) {
    const user = users.value.find(u => u.id === targetUserId)
    if (user) await selectUser(user)
  }
})

onUnmounted(() => {
  clearChatCallback()
})

const currentRole = localStorage.getItem('role')

async function loadUsers() {
  try {
    // HR/Manager see all users; candidates only see conversation partners
    const url = currentRole === 'candidate' ? '/users/conversations' : '/users/'
    const { data } = await api.get(url)
    users.value = data
  } catch {}
}

async function selectUser(user) {
  selectedUser.value = user
  loadingMessages.value = true
  offset.value = 0
  hasMore.value = true
  try {
    const { data } = await api.get(`/messages/${user.id}?limit=${limit}&offset=${offset.value}`)
    messages.value = data
    if (data.length < limit) hasMore.value = false
    // Mark messages as read
    await api.post(`/messages/read/${user.id}`)
    clearForUser(user.id)
  } catch {
    messages.value = []
  } finally {
    loadingMessages.value = false
    scrollToBottom()
  }
}

async function loadMoreMessages() {
  if (!selectedUser.value || loadingMore.value || !hasMore.value) return
  loadingMore.value = true
  offset.value += limit
  try {
    const { data } = await api.get(`/messages/${selectedUser.value.id}?limit=${limit}&offset=${offset.value}`)
    if (data.length < limit) hasMore.value = false
    messages.value = [...data, ...messages.value]
  } finally {
    loadingMore.value = false
  }
}

async function handleChatMessage(msg) {
  const otherId = msg.sender_id === currentUserId ? msg.receiver_id : msg.sender_id

  if (!users.value.find(u => u.id === otherId)) {
    await loadUsers()
    if (!selectedUser.value) {
      const newUser = users.value.find(u => u.id === otherId)
      if (newUser) await selectUser(newUser)
    }
  }

  if (selectedUser.value && selectedUser.value.id === otherId) {
    if (!messages.value.find(m => m.id === msg.id)) {
      messages.value.push(msg)
      scrollToBottom('smooth')
    }
    if (msg.sender_id !== currentUserId) {
      api.post(`/messages/read/${otherId}`).catch(() => {})
    }
  } else if (msg.sender_id !== currentUserId) {
    incrementForUser(otherId)
  }
}

function sendMessage() {
  const text = newMessage.value.trim()
  if (!text || !selectedUser.value) return
  const sent = sendWS({ receiver_id: selectedUser.value.id, text })
  if (sent) newMessage.value = ''
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

function scrollToBottom(behavior = 'auto') {
  nextTick(() => {
    messagesEnd.value?.scrollIntoView({ behavior })
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
  
  const firstUnread = messages.value.find(m => m.sender_id !== currentUserId && !m.is_read)
  const firstUnreadId = firstUnread ? firstUnread.id : null

  for (const msg of messages.value) {
    const date = formatDate(msg.created_at)
    if (date !== lastDate) {
      groups.push({ type: 'date', label: date })
      lastDate = date
    }
    if (msg.id === firstUnreadId) {
      groups.push({ type: 'unread_divider' })
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
          :disabled="selectedUser?.id === user.id"
          class="w-full flex items-center gap-3 px-4 py-3 transition-colors text-left border-b border-brand-light-border/50 dark:border-brand-dark-border/50"
          :class="selectedUser?.id === user.id ? 'bg-brand-accent/10 border-l-2 border-l-brand-accent cursor-default' : 'hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated'"
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
          <span
            v-if="unreadCounts[user.id]"
            class="min-w-[20px] h-5 rounded-full bg-brand-accent text-white text-[11px] font-bold flex items-center justify-center px-1.5 shrink-0 shadow-sm shadow-brand-accent/30"
          >
            {{ unreadCounts[user.id] }}
          </span>
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
        <div class="px-6 py-4 border-b border-brand-light-border dark:border-brand-dark-border bg-brand-light-surface dark:bg-brand-dark-surface flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-brand-accent/10 border border-brand-accent/20 flex items-center justify-center text-brand-accent text-xs font-bold shrink-0">
              {{ initials(selectedUser) }}
            </div>
            <div>
              <p class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-sm">{{ displayName(selectedUser) }}</p>
              <p class="text-micro" :class="ROLE_COLOR[selectedUser.role]">{{ ROLE_LABEL[selectedUser.role] }}</p>
            </div>
          </div>
          <router-link
            v-if="currentRole !== 'candidate' && selectedUser.role === 'candidate' && selectedUser.profile_id"
            :to="`/hr/candidates/${selectedUser.profile_id}`"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-brand-light-elevated dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border text-brand-accent text-xs font-bold hover:bg-brand-accent/10 transition-colors"
          >
            <User class="w-3.5 h-3.5" />
            Профиль
          </router-link>
        </div>

        <!-- Messages area -->
        <div class="flex-1 overflow-y-auto px-6 py-4 custom-scrollbar flex flex-col">
          <div v-if="loadingMessages" class="flex items-center justify-center h-full">
            <Loader2 class="w-8 h-8 animate-spin text-brand-accent/50" />
          </div>

          <template v-else>
            <div v-if="hasMore" class="flex justify-center shrink-0 mb-4 h-8 items-center">
              <button @click="loadMoreMessages" :disabled="loadingMore" class="flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-light-elevated dark:bg-brand-dark-elevated text-[11px] font-bold text-brand-light-secondary dark:text-brand-dark-secondary hover:text-brand-light-primary dark:hover:text-brand-dark-primary transition-colors border border-brand-light-border dark:border-brand-dark-border disabled:opacity-50">
                <Loader2 v-if="loadingMore" class="w-3.5 h-3.5 animate-spin text-brand-accent" />
                <span v-else>Загрузить предыдущие</span>
              </button>
            </div>
          
            <TransitionGroup appear name="bubble" tag="div" class="space-y-1 mt-auto shrink-0 pb-2 flex flex-col justify-end">
              <template v-for="(item, idx) in groupedMessages" :key="item.type === 'msg' ? item.msg.id : item.type + '-' + (item.label || '')">
                <!-- Date separator -->
                <div v-if="item.type === 'date'" class="flex items-center gap-3 py-3 w-full justify-center opacity-80" :style="{ transitionDelay: (idx * 30) + 'ms' }">
                  <div class="flex-1 max-w-[40px] h-px bg-brand-light-border dark:bg-brand-dark-border"></div>
                  <span class="text-[10px] uppercase font-bold tracking-widest text-brand-light-muted dark:text-brand-dark-muted px-2">{{ item.label }}</span>
                  <div class="flex-1 max-w-[40px] h-px bg-brand-light-border dark:bg-brand-dark-border"></div>
                </div>

                <!-- Unread separator -->
                <div v-else-if="item.type === 'unread_divider'" class="flex items-center justify-center py-5 relative w-full" :style="{ transitionDelay: (idx * 30) + 'ms' }">
                  <div class="absolute inset-0 flex items-center"><div class="w-full h-px bg-brand-status-new/30"></div></div>
                  <span class="relative bg-brand-light-surface dark:bg-brand-dark-surface px-4 py-1 rounded-full border border-brand-status-new/40 text-brand-status-new font-bold text-[10px] tracking-wider uppercase flex items-center gap-2 shadow-sm shadow-brand-status-new/10">
                    <MessageSquare class="w-3.5 h-3.5" />
                    Непрочитанные сообщения
                  </span>
                </div>

                <!-- Message bubble -->
                <div
                  v-else
                  class="flex w-full"
                  :class="item.msg.sender_id === currentUserId ? 'justify-end' : 'justify-start'"
                  :style="{ transitionDelay: (idx * 30) + 'ms' }"
                >
                  <div
                    class="max-w-[85%] lg:max-w-md px-4 py-2.5 rounded-2xl text-sm leading-relaxed"
                    :class="item.msg.sender_id === currentUserId
                      ? 'bg-brand-accent text-white rounded-br-sm shadow-sm shadow-brand-accent/20'
                      : 'bg-brand-light-surface dark:bg-brand-dark-elevated border border-brand-light-border dark:border-brand-dark-border text-brand-light-primary dark:text-brand-dark-primary rounded-bl-sm shadow-sm shadow-black/5'"
                  >
                    <p class="whitespace-pre-wrap break-words">{{ item.msg.text }}</p>
                    <p
                      class="text-[10px] font-medium mt-1 text-right tabular-nums h-3"
                      :class="item.msg.sender_id === currentUserId ? 'text-white/60' : 'text-brand-light-muted dark:text-brand-dark-muted'"
                    >
                      {{ formatTime(item.msg.created_at) }}
                    </p>
                  </div>
                </div>
              </template>
            </TransitionGroup>

            <!-- Empty conversation -->
            <div v-if="groupedMessages.length === 0" class="flex flex-col items-center justify-center h-full gap-2 text-center opacity-60">
              <p class="text-caption text-brand-light-secondary dark:text-brand-dark-secondary">Начните переписку с {{ displayName(selectedUser) }}</p>
            </div>

            <div ref="messagesEnd" class="h-0" />
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

.bubble-enter-active {
  animation: bubble-in 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.25) both;
}
.bubble-leave-active {
  position: absolute;
  opacity: 0;
}
.bubble-move {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes bubble-in {
  0% { transform: scale(0.9) translateY(10px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}
</style>
