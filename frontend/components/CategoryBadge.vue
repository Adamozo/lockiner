<script setup lang="ts">
type BadgeColor = 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'error' | 'neutral'

interface Props {
  category: string
  color?: string | null
  icon?: string | null
}

const props = defineProps<Props>()

// Default color mapping for common categories
const defaultColors: Record<string, BadgeColor> = {
  'Jedzenie': 'success',
  'Transport': 'primary',
  'Rozrywka': 'secondary',
  'Zdrowie': 'error',
  'Dom': 'warning',
  'Edukacja': 'info',
  'Inne': 'neutral',
}

const badgeColor = computed<BadgeColor>(() => {
  // If custom color is provided and it's one of the valid colors
  if (props.color && ['primary', 'secondary', 'success', 'info', 'warning', 'error', 'neutral'].includes(props.color)) {
    return props.color as BadgeColor
  }
  return defaultColors[props.category] || 'neutral'
})

const badgeIcon = computed(() => {
  if (props.icon) return props.icon

  // Default icons for common categories
  const defaultIcons: Record<string, string> = {
    'Jedzenie': 'i-heroicons-shopping-bag',
    'Transport': 'i-heroicons-truck',
    'Rozrywka': 'i-heroicons-film',
    'Zdrowie': 'i-heroicons-heart',
    'Dom': 'i-heroicons-home',
    'Edukacja': 'i-heroicons-academic-cap',
    'Inne': 'i-heroicons-tag',
  }

  return defaultIcons[props.category] || 'i-heroicons-tag'
})
</script>

<template>
  <UBadge
    :color="badgeColor"
    variant="solid"
    size="sm"
    class="backdrop-blur-sm transition-all duration-300 hover:shadow-lg"
    :class="{
      'hover:shadow-electric-green/30': badgeColor === 'success',
      'hover:shadow-cyber-blue/30': badgeColor === 'primary',
      'hover:shadow-danger-red/30': badgeColor === 'error',
      'hover:shadow-warning-orange/30': badgeColor === 'warning',
    }"
  >
    <div class="flex items-center space-x-1">
      <UIcon :name="badgeIcon" class="w-3 h-3" />
      <span>{{ category }}</span>
    </div>
  </UBadge>
</template>
