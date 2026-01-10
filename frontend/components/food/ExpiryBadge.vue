<script setup lang="ts">
/**
 * Expiry date badge with color coding
 */

interface Props {
  expiryDate: string | null
  showDays?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDays: true,
})

const daysUntilExpiry = computed(() => {
  if (!props.expiryDate) return null
  const expiry = new Date(props.expiryDate)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const diff = expiry.getTime() - today.getTime()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
})

const status = computed(() => {
  const days = daysUntilExpiry.value
  if (days === null) return 'unknown'
  if (days < 0) return 'expired'
  if (days <= 1) return 'danger'
  if (days <= 3) return 'warning'
  return 'ok'
})

const badgeClass = computed(() => {
  switch (status.value) {
    case 'expired':
      return 'bg-danger-red/20 text-danger-red border-danger-red/30'
    case 'danger':
      return 'bg-danger-red/10 text-danger-red border-danger-red/20'
    case 'warning':
      return 'bg-warning-orange/10 text-warning-orange border-warning-orange/20'
    case 'ok':
      return 'bg-electric-green/10 text-electric-green border-electric-green/20'
    default:
      return 'bg-pure-white/10 text-pure-white/60 border-pure-white/20'
  }
})

const label = computed(() => {
  const days = daysUntilExpiry.value
  if (days === null) return 'No date'
  if (days < 0) return `Expired ${Math.abs(days)}d ago`
  if (days === 0) return 'Today!'
  if (days === 1) return 'Tomorrow'
  return `${days} days`
})

const formattedDate = computed(() => {
  if (!props.expiryDate) return ''
  return new Date(props.expiryDate).toLocaleDateString('pl-PL', {
    day: 'numeric',
    month: 'short',
  })
})
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg border text-xs font-medium"
    :class="badgeClass"
  >
    <UIcon
      v-if="status === 'expired'"
      name="i-heroicons-x-circle"
      class="w-3.5 h-3.5"
    />
    <UIcon
      v-else-if="status === 'danger' || status === 'warning'"
      name="i-heroicons-exclamation-triangle"
      class="w-3.5 h-3.5"
    />
    <UIcon
      v-else-if="status === 'ok'"
      name="i-heroicons-check-circle"
      class="w-3.5 h-3.5"
    />
    <span v-if="showDays">{{ label }}</span>
    <span v-else>{{ formattedDate }}</span>
  </span>
</template>
