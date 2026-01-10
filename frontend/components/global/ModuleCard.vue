<script setup lang="ts">
interface Props {
  name: string
  description: string
  icon: string
  to: string
  color: 'electric-green' | 'warning-orange' | 'cyber-blue'
  stats?: { label: string; value: string | number }[]
}

const props = defineProps<Props>()

const colorClasses = computed(() => {
  switch (props.color) {
    case 'electric-green':
      return {
        icon: 'text-electric-green',
        border: 'hover:border-electric-green',
        shadow: 'hover:shadow-electric-green/20',
        gradient: 'from-electric-green/20 to-electric-green/5',
        statBorder: 'border-electric-green/30',
      }
    case 'warning-orange':
      return {
        icon: 'text-warning-orange',
        border: 'hover:border-warning-orange',
        shadow: 'hover:shadow-warning-orange/20',
        gradient: 'from-warning-orange/20 to-warning-orange/5',
        statBorder: 'border-warning-orange/30',
      }
    case 'cyber-blue':
    default:
      return {
        icon: 'text-cyber-blue',
        border: 'hover:border-cyber-blue',
        shadow: 'hover:shadow-cyber-blue/20',
        gradient: 'from-cyber-blue/20 to-cyber-blue/5',
        statBorder: 'border-cyber-blue/30',
      }
  }
})
</script>

<template>
  <NuxtLink
    :to="to"
    class="block bg-card-black border border-border-gray rounded-xl p-6 transition-all duration-300 hover:-translate-y-2 hover:shadow-xl group"
    :class="[colorClasses.border, colorClasses.shadow]"
  >
    <!-- Icon and Title -->
    <div class="flex items-start gap-4 mb-4">
      <div
        class="p-3 rounded-xl bg-gradient-to-br border"
        :class="[colorClasses.gradient, colorClasses.statBorder]"
      >
        <UIcon :name="icon" class="w-8 h-8" :class="colorClasses.icon" />
      </div>
      <div class="flex-1">
        <h3 class="text-xl font-bold text-pure-white group-hover:text-gradient-brand transition-colors">
          {{ name }}
        </h3>
        <p class="text-pure-white/60 text-sm mt-1">
          {{ description }}
        </p>
      </div>
      <UIcon
        name="i-heroicons-arrow-right"
        class="w-5 h-5 text-pure-white/40 group-hover:text-pure-white group-hover:translate-x-1 transition-all"
      />
    </div>

    <!-- Stats -->
    <div v-if="stats && stats.length > 0" class="grid grid-cols-2 gap-3 pt-4 border-t border-border-gray">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="text-center"
      >
        <p class="text-lg font-bold text-pure-white">{{ stat.value }}</p>
        <p class="text-xs text-pure-white/50">{{ stat.label }}</p>
      </div>
    </div>

    <!-- Empty State Placeholder -->
    <div v-else class="pt-4 border-t border-border-gray">
      <p class="text-sm text-pure-white/40 text-center">
        Click to get started
      </p>
    </div>
  </NuxtLink>
</template>
