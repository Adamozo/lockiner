<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  icon?: string
  loading?: boolean
  disabled?: boolean
  as?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
  as: 'button',
})

const buttonClasses = computed(() => {
  const base = 'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed'

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  }

  const variants = {
    primary: 'bg-gradient-to-r from-cyber-blue to-electric-green text-background-black hover:shadow-xl hover:shadow-cyber-blue/30 hover:-translate-y-1',
    secondary: 'border-2 border-border-gray bg-transparent text-pure-white hover:border-electric-green hover:shadow-lg hover:shadow-electric-green/20',
    danger: 'bg-gradient-to-r from-danger-red to-pink-500 text-white hover:shadow-xl hover:shadow-danger-red/30 hover:-translate-y-1',
    ghost: 'bg-transparent text-pure-white/70 hover:bg-white/5 hover:text-pure-white',
  }

  return [base, sizes[props.size], variants[props.variant]]
})
</script>

<template>
  <component
    :is="as"
    :class="buttonClasses"
    :disabled="as === 'button' ? (disabled || loading) : undefined"
  >
    <UIcon v-if="icon && !loading" :name="icon" class="w-5 h-5" />
    <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
    <slot />
  </component>
</template>
