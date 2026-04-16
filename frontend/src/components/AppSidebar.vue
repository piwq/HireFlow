<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useThemeStore } from '@/stores/theme.js'
import {
  Users,
  Briefcase,
  Calendar,
  FileText,
  Sun,
  Moon,
  LogOut,
  ChevronRight,
  X,
  MessageSquare,
} from 'lucide-vue-next'

const props = defineProps({
  open: Boolean
})
const emit = defineEmits(['close'])

const auth = useAuthStore()
const theme = useThemeStore()
const router = useRouter()
const route = useRoute()

const navItems = computed(() => {
  if (auth.role === 'hr') return [
    { label: 'Кандидаты', icon: Users, to: '/hr' },
    { label: 'Вакансии', icon: Briefcase, to: '/hr/vacancies' },
    { label: 'Чат', icon: MessageSquare, to: '/chat' },
  ]
  if (auth.role === 'manager') return [
    { label: 'Интервью', icon: Calendar, to: '/manager' },
    { label: 'Отзывы', icon: FileText, to: '/manager/reviews' },
    { label: 'Чат', icon: MessageSquare, to: '/chat' },
  ]
  return []
})

function logout() {
  auth.logout()
  router.push('/login')
}
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
            {{ auth.role === 'hr' ? 'HR Portal' : 'Management' }}
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
        <ChevronRight v-if="route.path === item.to" class="w-4 h-4" />
      </RouterLink>
    </nav>

    <!-- Bottom -->
    <div class="p-4 border-t border-brand-light-border dark:border-brand-dark-border space-y-1">
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
