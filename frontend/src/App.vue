<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme.js'
import AppLayout from '@/components/AppLayout.vue'

const theme = useThemeStore()
const route = useRoute()

// Only HR and Manager get the sidebar layout
const useLayout = computed(() => {
  const userRole = localStorage.getItem('role') || ''
  if (userRole !== 'hr' && userRole !== 'manager') return false
  const { role, roles } = route.meta
  if (role === 'hr' || role === 'manager') return true
  if (roles?.includes('hr') || roles?.includes('manager')) return true
  return false
})
</script>

<template>
  <div :class="{ 'dark': theme.dark }">
    <AppLayout v-if="useLayout">
      <RouterView />
    </AppLayout>
    <div v-else class="min-h-screen bg-brand-light-base dark:bg-brand-dark-base text-brand-light-primary dark:text-brand-dark-primary font-sans antialiased">
      <RouterView />
    </div>
  </div>
</template>
