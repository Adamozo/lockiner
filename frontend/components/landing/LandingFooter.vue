<script setup lang="ts">
// Landing page footer
</script>

<template>
  <footer class="border-t border-border-gray">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col md:flex-row justify-between items-center gap-4">
        <div class="flex items-center gap-3">
          <LockIcon class="w-8 h-8 text-electric-green" />
          <span class="text-lg font-bold"
            ><span class="text-cyber-blue">Lock</span
            ><span class="text-electric-green">In</span
            ><span class="text-pure-white">er</span></span
          >
        </div>
        <div class="flex flex-col items-center md:items-end gap-2">
          <div class="flex items-center gap-4">
            <NuxtLink
              to="/privacy-policy"
              class="text-pure-white/40 text-sm hover:text-cyber-blue transition-colors"
            >
              {{ $t('landing.footer_privacy') }}
            </NuxtLink>
            <span class="text-pure-white/20">|</span>
            <NuxtLink
              to="/terms"
              class="text-pure-white/40 text-sm hover:text-cyber-blue transition-colors"
            >
              {{ $t('landing.footer_terms') }}
            </NuxtLink>
            <span class="text-pure-white/20">|</span>
            <NuxtLink
              to="/changelog"
              class="text-pure-white/40 text-sm hover:text-cyber-blue transition-colors"
            >
              {{ $t('landing.footer_changelog') }}
            </NuxtLink>
          </div>
          <p class="text-pure-white/30 text-xs">
            &copy; {{ new Date().getFullYear() }} MAKE IT REMOTE
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>
