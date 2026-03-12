<script setup lang="ts">
import { BrowserMultiFormatReader } from '@zxing/browser'

const emit = defineEmits<{
  scanned: [code: string]
  close: []
}>()

const { t } = useI18n()
const videoRef = ref<HTMLVideoElement | null>(null)
const inputCode = ref('')
const errorMsg = ref('')
const controls = ref<any>(null)

async function startCamera() {
  if (!videoRef.value) return
  errorMsg.value = ''
  try {
    const reader = new BrowserMultiFormatReader()
    const devices = await BrowserMultiFormatReader.listVideoInputDevices()
    const backCamera = devices.find(d => /back|rear|environment/i.test(d.label)) || devices[devices.length - 1]
    const deviceId = backCamera?.deviceId

    controls.value = await reader.decodeFromVideoDevice(
      deviceId || undefined,
      videoRef.value,
      (result) => {
        if (result) {
          if (navigator.vibrate) navigator.vibrate(100)
          stopCamera()
          emit('scanned', result.getText())
        }
      }
    )
  } catch (e: any) {
    errorMsg.value = e?.message || 'Camera unavailable'
  }
}

function stopCamera() {
  if (controls.value) {
    controls.value.stop()
    controls.value = null
  }
}

function submitManual() {
  const code = inputCode.value.trim()
  if (code.length >= 8) emit('scanned', code)
}

function handleClose() {
  stopCamera()
  emit('close')
}

onMounted(startCamera)
onUnmounted(stopCamera)
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex flex-col bg-black">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 bg-background-black border-b border-border-gray">
        <h2 class="text-pure-white font-semibold text-lg">{{ $t('food.scan_title') }}</h2>
        <button class="p-1.5 text-gray-400 hover:text-pure-white transition-colors" @click="handleClose">
          <UIcon name="i-heroicons-x-mark" class="w-6 h-6" />
        </button>
      </div>

      <!-- Camera -->
      <div class="relative flex-1 overflow-hidden bg-black flex items-center justify-center">
        <video ref="videoRef" class="w-full h-full object-cover" autoplay muted playsinline />
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="w-64 h-32 relative">
            <div class="absolute top-0 left-0 w-7 h-7 border-t-4 border-l-4 border-electric-green rounded-tl" />
            <div class="absolute top-0 right-0 w-7 h-7 border-t-4 border-r-4 border-electric-green rounded-tr" />
            <div class="absolute bottom-0 left-0 w-7 h-7 border-b-4 border-l-4 border-electric-green rounded-bl" />
            <div class="absolute bottom-0 right-0 w-7 h-7 border-b-4 border-r-4 border-electric-green rounded-br" />
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-if="errorMsg" class="px-4 py-2 bg-danger-red/20 text-danger-red text-sm text-center">
        {{ errorMsg }}
      </div>

      <!-- Manual fallback -->
      <div class="p-4 bg-background-black border-t border-border-gray">
        <p class="text-gray-400 text-xs text-center mb-2">{{ $t('food.scan_manual') }}</p>
        <div class="flex gap-2">
          <input
            v-model="inputCode"
            type="text"
            placeholder="5901234123457"
            class="flex-1 px-3 py-2 bg-card-black border border-border-gray rounded-lg text-pure-white text-sm focus:outline-none focus:border-electric-green transition-colors"
            @keyup.enter="submitManual"
          />
          <BaseButton variant="primary" size="sm" :disabled="inputCode.trim().length < 8" @click="submitManual">
            {{ $t('food.search') }}
          </BaseButton>
        </div>
      </div>
    </div>
  </Teleport>
</template>
