<script setup>
import { ref } from 'vue'
import AppSidebar from './AppSidebar.vue'
import { Menu, X } from 'lucide-vue-next'

const sidebarOpen = ref(false)
</script>

<template>
  <div class="flex h-screen bg-brand-light-base dark:bg-brand-dark-base text-brand-light-primary dark:text-brand-dark-primary font-sans antialiased overflow-hidden">
    <!-- Mobile Header -->
    <div class="lg:hidden fixed top-0 left-0 right-0 h-16 bg-brand-light-surface dark:bg-brand-dark-surface border-b border-brand-light-border dark:border-brand-dark-border flex items-center justify-between px-6 z-40">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-lg bg-brand-accent flex items-center justify-center">
          <Menu class="w-5 h-5 text-white" />
        </div>
        <span class="font-bold text-lg">HireFlow</span>
      </div>
      <button 
        @click="sidebarOpen = !sidebarOpen"
        class="p-2 rounded-xl bg-brand-light-elevated dark:bg-brand-dark-elevated text-brand-light-secondary dark:text-brand-dark-secondary"
      >
        <component :is="sidebarOpen ? X : Menu" class="w-6 h-6" />
      </button>
    </div>

    <AppSidebar :open="sidebarOpen" @close="sidebarOpen = false" />
    
    <main class="flex-1 overflow-auto pt-16 lg:pt-0">
      <slot />
    </main>
  </div>
</template>
