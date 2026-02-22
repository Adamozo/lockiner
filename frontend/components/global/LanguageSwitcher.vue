<script setup lang="ts">
const { locale, changeLanguage } = useLanguage()
</script>

<template>
  <div class="flex items-center gap-1">
    <button
      :class="[
        'px-2 py-1 text-xs font-bold rounded transition-colors',
        locale === 'en'
          ? 'text-cyber-blue border border-cyber-blue bg-cyber-blue/10'
          : 'text-pure-white/50 hover:text-pure-white border border-transparent',
      ]"
      @click="changeLanguage('en')"
    >
      EN
    </button>
    <button
      :class="[
        'px-2 py-1 text-xs font-bold rounded transition-colors',
        locale === 'pl'
          ? 'text-cyber-blue border border-cyber-blue bg-cyber-blue/10'
          : 'text-pure-white/50 hover:text-pure-white border border-transparent',
      ]"
      @click="changeLanguage('pl')"
    >
      PL
    </button>
  </div>
</template>
