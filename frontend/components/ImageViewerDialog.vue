<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean
  imageUrl: string
  title?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// Zoom state
const zoomLevel = ref(1)
const minZoom = 0.5
const maxZoom = 3
const zoomStep = 0.25

// Pan state
const isPanning = ref(false)
const panX = ref(0)
const panY = ref(0)
const startX = ref(0)
const startY = ref(0)

// Reset state when dialog opens/closes
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    resetView()
  }
})

// Reset view to default
const resetView = () => {
  zoomLevel.value = 1
  panX.value = 0
  panY.value = 0
}

// Zoom controls
const zoomIn = () => {
  if (zoomLevel.value < maxZoom) {
    zoomLevel.value = Math.min(maxZoom, zoomLevel.value + zoomStep)
  }
}

const zoomOut = () => {
  if (zoomLevel.value > minZoom) {
    zoomLevel.value = Math.max(minZoom, zoomLevel.value - zoomStep)
    // Reset pan when zooming out to 1x or less
    if (zoomLevel.value <= 1) {
      panX.value = 0
      panY.value = 0
    }
  }
}

// Pan controls
const handleMouseDown = (e: MouseEvent) => {
  if (zoomLevel.value > 1) {
    isPanning.value = true
    startX.value = e.clientX - panX.value
    startY.value = e.clientY - panY.value
  }
}

const handleMouseMove = (e: MouseEvent) => {
  if (isPanning.value) {
    panX.value = e.clientX - startX.value
    panY.value = e.clientY - startY.value
  }
}

const handleMouseUp = () => {
  isPanning.value = false
}

// Close dialog
const close = () => {
  emit('update:modelValue', false)
}

// Keyboard shortcuts
const handleKeydown = (e: KeyboardEvent) => {
  if (!props.modelValue) return

  switch (e.key) {
    case 'Escape':
      close()
      break
    case '+':
    case '=':
      e.preventDefault()
      zoomIn()
      break
    case '-':
    case '_':
      e.preventDefault()
      zoomOut()
      break
    case '0':
      e.preventDefault()
      resetView()
      break
  }
}

// Setup keyboard listener
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

// Image transform style
const imageStyle = computed(() => ({
  transform: `scale(${zoomLevel.value}) translate(${panX.value / zoomLevel.value}px, ${panY.value / zoomLevel.value}px)`,
  cursor: zoomLevel.value > 1 ? (isPanning.value ? 'grabbing' : 'grab') : 'default',
}))

// Zoom percentage
const zoomPercentage = computed(() => Math.round(zoomLevel.value * 100))
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-[100] bg-background-black/95 backdrop-blur-sm"
        @click.self="close"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        @mouseleave="handleMouseUp"
      >
        <!-- Header -->
        <div class="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4 bg-gradient-to-b from-background-black/80 to-transparent">
          <div>
            <h2 v-if="title" class="text-lg font-semibold text-pure-white">
              {{ title }}
            </h2>
            <p class="text-sm text-pure-white/60">
              Press ESC to close • +/- to zoom • Drag to pan
            </p>
          </div>
          <button
            class="p-2 rounded-lg bg-card-black/80 border border-border-gray text-pure-white hover:bg-danger-red hover:border-danger-red transition-all duration-200"
            @click="close"
          >
            <UIcon name="i-heroicons-x-mark" class="w-6 h-6" />
          </button>
        </div>

        <!-- Image Container -->
        <div class="absolute inset-0 flex items-center justify-center p-20">
          <img
            :src="imageUrl"
            :alt="title || 'Receipt image'"
            class="max-w-full max-h-full object-contain transition-transform duration-200 select-none"
            :style="imageStyle"
            draggable="false"
            @mousedown="handleMouseDown"
          />
        </div>

        <!-- Controls -->
        <div class="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-10">
          <div class="flex items-center gap-3 bg-card-black/90 backdrop-blur-md border border-border-gray rounded-full px-4 py-3 shadow-2xl">
            <!-- Zoom Out -->
            <button
              class="p-2 rounded-full hover:bg-cyber-blue/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              :disabled="zoomLevel <= minZoom"
              @click="zoomOut"
            >
              <UIcon name="i-heroicons-minus" class="w-5 h-5 text-pure-white" />
            </button>

            <!-- Zoom Level -->
            <div class="min-w-[80px] text-center">
              <span class="text-sm font-semibold text-pure-white">
                {{ zoomPercentage }}%
              </span>
            </div>

            <!-- Zoom In -->
            <button
              class="p-2 rounded-full hover:bg-cyber-blue/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              :disabled="zoomLevel >= maxZoom"
              @click="zoomIn"
            >
              <UIcon name="i-heroicons-plus" class="w-5 h-5 text-pure-white" />
            </button>

            <!-- Divider -->
            <div class="h-6 w-px bg-border-gray" />

            <!-- Reset -->
            <button
              class="p-2 rounded-full hover:bg-cyber-blue/20 transition-colors"
              title="Reset view (Press 0)"
              @click="resetView"
            >
              <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 text-pure-white" />
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
