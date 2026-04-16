<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import AppSidebar from './AppSidebar.vue'
import { Menu, X } from 'lucide-vue-next'
import { connectWS, disconnectWS } from '@/stores/ws.js'
import { useNotificationsStore } from '@/stores/notifications.js'

const sidebarOpen = ref(false)
const notifications = useNotificationsStore()

// Toast state
const toast = ref(null)
let toastTimer = null

onMounted(connectWS)
onUnmounted(disconnectWS)

// Show toast on new notification
watch(
  () => notifications.items[0],
  (n) => {
    if (!n || n.read) return
    toast.value = n
    clearTimeout(toastTimer)
    toastTimer = setTimeout(() => { toast.value = null }, 4500)
  }
)
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

    <main class="flex-1 overflow-auto pt-16 lg:pt-0 flex flex-col">
      <slot />
    </main>

    <!-- Toast notification -->
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <div
        v-if="toast"
        class="fixed bottom-6 right-6 z-[100] flex items-start gap-3 bg-brand-light-surface dark:bg-brand-dark-surface border border-brand-light-border dark:border-brand-dark-border rounded-2xl shadow-2xl shadow-black/20 p-4 max-w-sm cursor-pointer"
        @click="toast = null"
      >
        <span class="text-xl shrink-0 mt-0.5">{{ toast.icon }}</span>
        <div class="min-w-0">
          <p class="text-sm font-semibold text-brand-light-primary dark:text-brand-dark-primary leading-snug">{{ toast.text }}</p>
          <p class="text-xs text-brand-light-muted dark:text-brand-dark-muted mt-0.5">Только что</p>
        </div>
        <button class="shrink-0 text-brand-light-muted dark:text-brand-dark-muted hover:text-brand-light-primary dark:hover:text-brand-dark-primary">
          <X class="w-4 h-4" />
        </button>
      </div>
    </Transition>
  </div>
</template>
