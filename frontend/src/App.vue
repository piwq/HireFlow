<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme.js'
import AppLayout from '@/components/AppLayout.vue'

const theme = useThemeStore()
const route = useRoute()

// HR, Manager and Candidate get the sidebar layout
const useLayout = computed(() => {
  const userRole = localStorage.getItem('role') || ''
  if (!['hr', 'manager', 'candidate', 'admin'].includes(userRole)) return false
  const { role, roles, guest } = route.meta
  if (guest) return false
  if (['hr', 'manager', 'candidate', 'admin'].includes(role)) return true
  if (roles?.some(r => ['hr', 'manager', 'candidate', 'admin'].includes(r))) return true
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
