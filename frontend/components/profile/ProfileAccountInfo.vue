<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()

const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>

<template>
  <div class="bg-card-black border border-border-gray rounded-lg shadow overflow-hidden">
    <div class="px-6 py-4 border-b border-border-gray relative">
      <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green" />
      <h2 class="text-xl font-semibold text-pure-white">Account Information</h2>
    </div>

    <div class="px-6 py-6">
      <div class="flex items-center gap-6">
        <!-- Avatar -->
        <div class="w-20 h-20 rounded-full bg-gradient-to-br from-cyber-blue to-electric-green flex items-center justify-center text-3xl font-bold text-background-black">
          {{ authStore.userName?.charAt(0)?.toUpperCase() || '?' }}
        </div>

        <!-- Info -->
        <div class="flex-1 space-y-2">
          <div>
            <span class="text-sm text-pure-white/60">Name</span>
            <p class="text-lg font-medium text-pure-white">{{ authStore.userName }}</p>
          </div>
          <div>
            <span class="text-sm text-pure-white/60">Email</span>
            <p class="text-pure-white">{{ authStore.userEmail }}</p>
          </div>
          <div>
            <span class="text-sm text-pure-white/60">Member since</span>
            <p class="text-pure-white">{{ formatDate(authStore.user?.created_at || null) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
