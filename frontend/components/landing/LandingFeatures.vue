<script setup lang="ts">
const { t } = useI18n()

const valueProps = computed(() => [
  { icon: "i-heroicons-chart-bar-square", color: "electric-green" as const, title: t('landing.vp1_title'), description: t('landing.vp1_desc') },
  { icon: "i-heroicons-bell-alert",       color: "warning-orange" as const, title: t('landing.vp2_title'), description: t('landing.vp2_desc') },
  { icon: "i-heroicons-device-phone-mobile", color: "cyber-blue" as const,  title: t('landing.vp3_title'), description: t('landing.vp3_desc') },
  { icon: "i-heroicons-lock-closed",      color: "electric-green" as const, title: t('landing.vp4_title'), description: t('landing.vp4_desc') },
  { icon: "i-heroicons-squares-2x2",      color: "cyber-blue" as const,     title: t('landing.vp5_title'), description: t('landing.vp5_desc') },
  { icon: "i-heroicons-users",            color: "warning-orange" as const, title: t('landing.vp6_title'), description: t('landing.vp6_desc') },
])

const colorClasses = {
  "electric-green": { bg: "bg-electric-green/10", text: "text-electric-green", border: "border-electric-green/15" },
  "warning-orange": { bg: "bg-warning-orange/10", text: "text-warning-orange", border: "border-warning-orange/15" },
  "cyber-blue":     { bg: "bg-cyber-blue/10",     text: "text-cyber-blue",     border: "border-cyber-blue/15" },
}

const modules = computed(() => [
  { name: t('nav.finance'),    icon: "i-heroicons-banknotes",     color: "electric-green" as const },
  { name: t('nav.fitness'),    icon: "i-heroicons-fire",          color: "warning-orange" as const },
  { name: t('nav.food'),       icon: "i-heroicons-cake",          color: "electric-green" as const },
  { name: t('nav.journal'),    icon: "i-heroicons-pencil-square", color: "cyber-blue" as const },
  { name: t('nav.households'), icon: "i-heroicons-home-modern",   color: "cyber-blue" as const },
])
</script>

<template>
  <div class="border-t border-border-gray">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">

      <!-- Header -->
      <div class="max-w-3xl mb-14 md:mb-16">
        <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold text-pure-white leading-tight mb-5">
          {{ $t('landing.features_heading') }}<br class="hidden sm:block" />
          {{ $t('landing.features_heading2') }}
        </h2>
        <p class="text-pure-white/55 text-lg leading-relaxed">
          {{ $t('landing.features_sub') }}
        </p>
      </div>

      <!-- Value props grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div
          v-for="vp in valueProps"
          :key="vp.title"
          class="bg-card-black border rounded-2xl p-7 flex flex-col gap-4 hover:border-white/15 transition-colors"
          :class="colorClasses[vp.color].border"
        >
          <div
            class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
            :class="colorClasses[vp.color].bg"
          >
            <UIcon :name="vp.icon" class="w-5 h-5" :class="colorClasses[vp.color].text" />
          </div>
          <div>
            <h3 class="text-base font-bold text-pure-white mb-2 leading-snug">{{ vp.title }}</h3>
            <p class="text-pure-white/55 text-sm leading-relaxed">{{ vp.description }}</p>
          </div>
        </div>
      </div>

      <!-- Module chips -->
      <div class="mt-14 pt-10 border-t border-border-gray">
        <p class="text-xs font-bold tracking-widest uppercase text-pure-white/35 mb-5">
          {{ $t('landing.features_modules_label') }}
        </p>
        <div class="flex flex-wrap gap-3">
          <div
            v-for="mod in modules"
            :key="mod.name"
            class="flex items-center gap-2 px-4 py-2 bg-card-black border border-border-gray rounded-full text-sm font-medium text-pure-white/70"
          >
            <UIcon :name="mod.icon" class="w-4 h-4" :class="colorClasses[mod.color].text" />
            {{ mod.name }}
          </div>
        </div>
      </div>

    </div>
  </div>
</template>
