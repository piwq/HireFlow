<script setup>
import AppSidebar from './AppSidebar.vue'
</script>

<template>
  <div class="flex h-screen bg-slate-50 dark:bg-[#0D0F1A]">
    <AppSidebar />
    <main class="flex-1 overflow-auto">
      <slot />
    </main>
  </div>
</template>
