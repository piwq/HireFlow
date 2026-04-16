<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useThemeStore } from '@/stores/theme.js'
import { unreadCounts, loadUnreadCounts, getTotalUnread } from '@/stores/unread.js'
import { useNotificationsStore } from '@/stores/notifications.js'
import {
  Users,
  User,
  Briefcase,
  Calendar,
  FileText,
  ClipboardList,
  Video,
  Sun,
  Moon,
  LogOut,
  ChevronRight,
  X,
  MessageSquare,
  Wand2,
  Bell,
} from 'lucide-vue-next'

const props = defineProps({
  open: Boolean
})
const emit = defineEmits(['close'])

const auth = useAuthStore()
const theme = useThemeStore()
const router = useRouter()
const route = useRoute()
const notificationsStore = useNotificationsStore()
const showNotifications = ref(false)

const navItems = computed(() => {
  if (auth.role === 'hr') return [
    { label: 'Кандидаты', icon: Users, to: '/hr' },
    { label: 'Вакансии', icon: Briefcase, to: '/hr/vacancies' },
    { label: 'Запросы интервью', icon: ClipboardList, to: '/hr/interview-requests' },
    { label: 'Чат', icon: MessageSquare, to: '/chat' },
  ]
  if (auth.role === 'manager') return [
    { label: 'Кандидаты', icon: Users, to: '/manager/candidates' },
    { label: 'Интервью', icon: Calendar, to: '/manager' },
    { label: 'Отзывы', icon: FileText, to: '/manager/reviews' },
    { label: 'Чат', icon: MessageSquare, to: '/chat' },
  ]
  if (auth.role === 'candidate') return [
    { label: 'Профиль', icon: User, to: '/candidate' },
    { label: 'ИИ Конструктор', icon: Wand2, to: '/candidate/resume-builder' },
    { label: 'Мои заявки', icon: ClipboardList, to: '/candidate/applications' },
    { label: 'Собеседования', icon: Video, to: '/candidate/interviews' },
    { label: 'Чат', icon: MessageSquare, to: '/chat' },
  ]
  if (auth.role === 'admin') return [
    { label: 'Панель администратора', icon: Users, to: '/admin' },
    { label: 'Чат', icon: MessageSquare, to: '/chat' },
  ]
  return []
})

function logout() {
  auth.logout()
  router.push('/login')
}

const totalUnread = computed(() => getTotalUnread())

let pollInterval = null
onMounted(() => {
  loadUnreadCounts()
  pollInterval = setInterval(loadUnreadCounts, 30000)
})
onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<template>
  <!-- Mobile Overlay -->
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-300"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div 
      v-if="open" 
      @click="emit('close')"
      class="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
    ></div>
  </Transition>

  <aside 
    class="fixed lg:static inset-y-0 left-0 w-64 shrink-0 h-screen flex flex-col bg-brand-light-surface dark:bg-brand-dark-surface border-r border-brand-light-border dark:border-brand-dark-border z-50 transition-transform duration-300 lg:translate-x-0 antialiased"
    :class="open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
  >
    <!-- Logo -->
    <div class="px-6 py-6 border-b border-brand-light-border dark:border-brand-dark-border flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-brand-accent flex items-center justify-center shadow-lg shadow-brand-accent/30">
          <Briefcase class="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 class="font-bold text-brand-light-primary dark:text-brand-dark-primary text-xl leading-none tracking-tight">HireFlow</h1>
          <p class="text-micro text-brand-light-secondary dark:text-brand-dark-secondary mt-1 uppercase tracking-wider">
            {{ auth.role === 'hr' ? 'HR Portal' : auth.role === 'candidate' ? 'Candidate Portal' : auth.role === 'admin' ? 'Admin Panel' : 'Management' }}
          </p>
        </div>
      </div>
      <button @click="emit('close')" class="lg:hidden p-1 rounded-lg hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated text-brand-light-muted dark:text-brand-dark-muted">
        <X class="w-5 h-5" />
      </button>
    </div>

    <!-- Nav -->
    <nav class="flex-1 p-4 space-y-1">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        @click="emit('close')"
        class="group flex items-center gap-3 px-3 py-2.5 rounded-lg text-body font-medium transition-all duration-200"
        :class="route.path === item.to
          ? 'bg-brand-accent/10 text-brand-accent shadow-sm shadow-brand-accent/5'
          : 'text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated hover:text-brand-light-primary dark:hover:text-brand-dark-primary'"
      >
        <component :is="item.icon" class="w-4.5 h-4.5" :class="route.path === item.to ? 'text-brand-accent' : 'text-brand-light-muted dark:text-brand-dark-muted group-hover:text-brand-light-primary dark:group-hover:text-brand-dark-primary'" />
        <span class="flex-1">{{ item.label }}</span>
        <span
          v-if="item.to === '/chat' && totalUnread > 0"
          class="min-w-[20px] h-5 rounded-full bg-brand-accent text-white text-[11px] font-bold flex items-center justify-center px-1.5 shadow-sm shadow-brand-accent/30"
        >
          {{ totalUnread > 99 ? '99+' : totalUnread }}
        </span>
        <ChevronRight v-if="route.path === item.to" class="w-4 h-4" />
      </RouterLink>
    </nav>

    <!-- Notifications panel -->
    <div v-if="showNotifications" class="mx-3 mb-2 bg-brand-light-elevated dark:bg-brand-dark-elevated rounded-xl border border-brand-light-border dark:border-brand-dark-border overflow-hidden">
      <div class="flex items-center justify-between px-3 py-2 border-b border-brand-light-border dark:border-brand-dark-border">
        <span class="text-xs font-bold text-brand-light-primary dark:text-brand-dark-primary uppercase tracking-wider">Уведомления</span>
        <button
          v-if="notificationsStore.unreadCount > 0"
          @click="notificationsStore.markAllRead()"
          class="text-xs text-brand-accent hover:underline"
        >Прочитать все</button>
      </div>
      <div class="max-h-64 overflow-y-auto">
        <div v-if="notificationsStore.items.length === 0" class="px-3 py-4 text-xs text-brand-light-muted dark:text-brand-dark-muted text-center">
          Нет уведомлений
        </div>
        <div
          v-for="n in notificationsStore.items.slice(0, 15)"
          :key="n.id"
          :class="['flex items-start gap-2 px-3 py-2.5 border-b border-brand-light-border dark:border-brand-dark-border last:border-0 transition-colors', n.read ? 'opacity-60' : 'bg-brand-accent/5']"
        >
          <span class="text-base shrink-0 mt-0.5">{{ n.icon }}</span>
          <div class="min-w-0 flex-1">
            <p class="text-xs text-brand-light-primary dark:text-brand-dark-primary leading-snug">{{ n.text }}</p>
            <p class="text-[10px] text-brand-light-muted dark:text-brand-dark-muted mt-0.5">
              {{ n.at.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) }}
            </p>
          </div>
          <div v-if="!n.read" class="w-1.5 h-1.5 rounded-full bg-brand-accent shrink-0 mt-1.5"></div>
        </div>
      </div>
    </div>

    <!-- Bottom -->
    <div class="p-4 border-t border-brand-light-border dark:border-brand-dark-border space-y-1">
      <button
        @click="showNotifications = !showNotifications; if (showNotifications) notificationsStore.markAllRead()"
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-body font-medium text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated hover:text-brand-light-primary dark:hover:text-brand-dark-primary transition-colors group"
      >
        <div class="relative">
          <Bell class="w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted group-hover:text-brand-light-primary dark:group-hover:text-brand-dark-primary" />
          <span
            v-if="notificationsStore.unreadCount > 0"
            class="absolute -top-1.5 -right-1.5 min-w-[16px] h-4 rounded-full bg-red-500 text-white text-[9px] font-bold flex items-center justify-center px-0.5"
          >{{ notificationsStore.unreadCount > 9 ? '9+' : notificationsStore.unreadCount }}</span>
        </div>
        <span class="flex-1 text-left">Уведомления</span>
      </button>
      <button
        @click="theme.toggle()"
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-body font-medium text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-brand-light-elevated dark:hover:bg-brand-dark-elevated hover:text-brand-light-primary dark:hover:text-brand-dark-primary transition-colors group"
      >
        <component :is="theme.dark ? Sun : Moon" class="w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted group-hover:text-brand-light-primary dark:group-hover:text-brand-dark-primary" />
        {{ theme.dark ? 'Светлая тема' : 'Тёмная тема' }}
      </button>
      <button
        @click="logout(); emit('close')"
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-body font-medium text-brand-light-secondary dark:text-brand-dark-secondary hover:bg-red-500/10 hover:text-red-500 transition-colors group"
      >
        <LogOut class="w-4.5 h-4.5 text-brand-light-muted dark:text-brand-dark-muted group-hover:text-red-500" />
        Выход
      </button>
    </div>
  </aside>
</template>
