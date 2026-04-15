<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useThemeStore } from '@/stores/theme.js'

const auth = useAuthStore()
const theme = useThemeStore()
const router = useRouter()
const route = useRoute()

const navItems = computed(() => {
  if (auth.role === 'hr') return [
    { label: 'Кандидаты', icon: '👥', to: '/hr' },
  ]
  if (auth.role === 'manager') return [
    { label: 'Собеседования', icon: '📅', to: '/manager' },
  ]
  return []
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <aside class="w-60 shrink-0 h-screen flex flex-col bg-white dark:bg-[#151827] border-r border-slate-200 dark:border-[#2A2F4A]">
    <!-- Logo -->
    <div class="px-5 py-5 border-b border-slate-200 dark:border-[#2A2F4A]">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
          <span class="text-white text-sm font-bold">H</span>
        </div>
        <span class="font-bold text-slate-900 dark:text-slate-100 text-lg tracking-tight">HireFlow</span>
      </div>
      <p class="text-xs text-slate-400 dark:text-slate-600 mt-1 pl-[42px]">
        {{ auth.role === 'hr' ? 'HR-специалист' : 'Руководитель' }}
      </p>
    </div>

    <!-- Nav -->
    <nav class="flex-1 p-3 space-y-0.5">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
        :class="route.path === item.to
          ? 'bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400'
          : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200'"
      >
        <span class="text-base leading-none">{{ item.icon }}</span>
        {{ item.label }}
      </RouterLink>
    </nav>

    <!-- Bottom -->
    <div class="p-3 border-t border-slate-200 dark:border-[#2A2F4A] space-y-0.5">
      <button
        @click="theme.toggle()"
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
      >
        <span class="text-base leading-none">{{ theme.dark ? '☀️' : '🌙' }}</span>
        {{ theme.dark ? 'Светлая тема' : 'Тёмная тема' }}
      </button>
      <button
        @click="logout()"
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600 dark:hover:text-red-400 transition-colors"
      >
        <span class="text-base leading-none">↩</span>
        Выйти
      </button>
    </div>
  </aside>
</template>
