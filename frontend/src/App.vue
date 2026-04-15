<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme.js'
import AppLayout from '@/components/AppLayout.vue'

const theme = useThemeStore()
const route = useRoute()

// Candidate doesn't have sidebar as per Brandbook
const useLayout = computed(() => {
  return route.meta.role === 'hr' || route.meta.role === 'manager'
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
