<script setup lang="ts">
// Landing page navigation bar
const mobileMenuOpen = ref(false)
</script>

<template>
  <nav class="border-b border-border-gray">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-14 sm:h-16">
        <NuxtLink to="/" class="flex items-center gap-2 sm:gap-3 group">
          <LockIcon class="w-8 h-8 sm:w-10 sm:h-10 text-electric-green group-hover:scale-110 transition-transform" />
          <span class="text-xl font-bold">
            <span class="text-cyber-blue">Lock</span>
            <span class="text-electric-green">In</span>
            <span class="text-pure-white">er</span>
          </span>
        </NuxtLink>

        <!-- Desktop nav -->
        <div class="hidden sm:flex items-center gap-4">
          <LanguageSwitcher />
          <NuxtLink
            to="/changelog"
            class="text-pure-white/50 hover:text-pure-white transition-colors text-sm font-medium"
          >
            {{ $t('landing.nav_changelog') }}
          </NuxtLink>
          <NuxtLink
            to="/login"
            class="text-pure-white/70 hover:text-pure-white transition-colors font-medium"
          >
            {{ $t('landing.nav_sign_in') }}
          </NuxtLink>
          <NuxtLink
            to="/register"
            class="px-4 py-2 bg-electric-green hover:bg-electric-green/90 text-background-black font-semibold rounded-lg transition-colors"
          >
            {{ $t('landing.nav_get_started') }}
          </NuxtLink>
        </div>

        <!-- Mobile: Hamburger -->
        <button
          class="flex sm:hidden p-2 rounded-lg text-pure-white/70 hover:text-pure-white hover:bg-card-black/50 transition-colors"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <UIcon
            :name="mobileMenuOpen ? 'i-heroicons-x-mark' : 'i-heroicons-bars-3'"
            class="w-6 h-6"
          />
        </button>
      </div>

      <!-- Mobile dropdown -->
      <div v-if="mobileMenuOpen" class="sm:hidden pb-4 pt-2 border-t border-border-gray space-y-3">
        <div class="flex items-center justify-between px-1">
          <span class="text-xs font-medium text-pure-white/40 uppercase tracking-wider">{{ $t('settings.language') }}</span>
          <LanguageSwitcher />
        </div>
        <div class="border-t border-border-gray" />
        <NuxtLink
          to="/changelog"
          class="block px-1 py-2 text-pure-white/70 hover:text-pure-white transition-colors text-sm font-medium"
          @click="mobileMenuOpen = false"
        >
          {{ $t('landing.nav_changelog') }}
        </NuxtLink>
        <NuxtLink
          to="/login"
          class="block px-1 py-2 text-pure-white/70 hover:text-pure-white transition-colors font-medium"
          @click="mobileMenuOpen = false"
        >
          {{ $t('landing.nav_sign_in') }}
        </NuxtLink>
        <NuxtLink
          to="/register"
          class="block px-1 py-2 text-electric-green hover:text-electric-green/80 transition-colors font-semibold"
          @click="mobileMenuOpen = false"
        >
          {{ $t('landing.nav_get_started') }}
        </NuxtLink>
      </div>
    </div>
  </nav>
</template>
