<script setup lang="ts">
const toast = useToast()
const timers = new Map<string | number, ReturnType<typeof setTimeout>>()

// Nuxt UI v3 useToast() exposes a reactive `toasts` ref
const toasts = computed(() => toast.toasts?.value ?? [])

watch(toasts, (list) => {
  for (const t of list) {
    if (!timers.has(t.id)) {
      console.log('[AppToasts] new toast detected:', t.id, t.title)
      const timer = setTimeout(() => {
        toast.remove(t.id)
        timers.delete(t.id)
      }, 4000)
      timers.set(t.id, timer)
    }
  }
  // clean up timers for removed toasts
  for (const id of timers.keys()) {
    if (!list.find((t: any) => t.id === id)) {
      timers.delete(id)
    }
  }
}, { deep: true, immediate: true })

const dismiss = (id: string | number) => {
  const timer = timers.get(id)
  if (timer) {
    clearTimeout(timer)
    timers.delete(id)
  }
  toast.remove(id)
}

const iconFor = (color?: string) => {
  switch (color) {
    case 'green': return 'i-heroicons-check-circle'
    case 'red': return 'i-heroicons-x-circle'
    case 'orange': return 'i-heroicons-exclamation-triangle'
    default: return 'i-heroicons-information-circle'
  }
}

onUnmounted(() => {
  for (const timer of timers.values()) {
    clearTimeout(timer)
  }
  timers.clear()
})
</script>

<template>
  <Teleport to="body">
    <div class="fixed bottom-4 left-4 right-4 z-[100] flex flex-col gap-3 pointer-events-none md:left-auto md:max-w-sm">
      <TransitionGroup
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="translate-x-full opacity-0"
        enter-to-class="translate-x-0 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="translate-x-0 opacity-100"
        leave-to-class="translate-x-full opacity-0"
      >
        <div
          v-for="t in toasts"
          :key="t.id"
          class="pointer-events-auto bg-card-black border rounded-lg shadow-lg p-4 flex items-start gap-3"
          :class="{
            'border-electric-green/40 shadow-electric-green/10': t.color === 'green',
            'border-danger-red/40 shadow-danger-red/10': t.color === 'red',
            'border-warning-orange/40 shadow-warning-orange/10': t.color === 'orange',
            'border-cyber-blue/40 shadow-cyber-blue/10': !t.color || t.color === 'blue',
          }"
        >
          <UIcon
            :name="iconFor(t.color)"
            class="w-5 h-5 flex-shrink-0 mt-0.5"
            :class="{
              'text-electric-green': t.color === 'green',
              'text-danger-red': t.color === 'red',
              'text-warning-orange': t.color === 'orange',
              'text-cyber-blue': !t.color || t.color === 'blue',
            }"
          />
          <div class="flex-1 min-w-0">
            <p
              class="text-sm font-semibold"
              :class="{
                'text-electric-green': t.color === 'green',
                'text-danger-red': t.color === 'red',
                'text-warning-orange': t.color === 'orange',
                'text-cyber-blue': !t.color || t.color === 'blue',
              }"
            >
              {{ t.title }}
            </p>
            <p v-if="t.description" class="mt-1 text-xs text-pure-white/60">
              {{ t.description }}
            </p>
          </div>
          <button
            class="flex-shrink-0 text-pure-white/40 hover:text-pure-white transition-colors"
            @click="dismiss(t.id)"
          >
            <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
