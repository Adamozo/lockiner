<script setup lang="ts">
import QRCode from 'qrcode'

const props = defineProps<{
  value: string
}>()

const qrDataUrl = ref<string>('')

const generateQR = async () => {
  if (!props.value) return
  try {
    qrDataUrl.value = await QRCode.toDataURL(props.value, {
      width: 200,
      margin: 2,
      color: {
        dark: '#FFFFFF',
        light: '#000000',
      },
    })
  } catch (err) {
    console.error('Failed to generate QR code:', err)
  }
}

watch(() => props.value, generateQR, { immediate: true })
</script>

<template>
  <div class="flex justify-center">
    <img
      v-if="qrDataUrl"
      :src="qrDataUrl"
      alt="QR Code for authenticator app"
      class="rounded-lg border border-border-gray"
    />
    <div
      v-else
      class="w-[200px] h-[200px] rounded-lg border border-border-gray bg-background-black flex items-center justify-center"
    >
      <UIcon name="i-heroicons-qr-code" class="w-8 h-8 text-pure-white/40" />
    </div>
  </div>
</template>
