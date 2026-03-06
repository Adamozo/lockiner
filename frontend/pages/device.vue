<script setup lang="ts">
import { useApi } from '~/composables/useApi'

definePageMeta({
  layout: 'default',
})

useSeoMeta({
  title: 'Autoryzacja urządzenia - LockIner',
})

const api = useApi()
const toast = useToast()

const userCode = ref('')
const loading = ref(false)
const done = ref<'approved' | 'denied' | null>(null)

const formattedCode = computed(() => {
  const raw = userCode.value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase()
  if (raw.length > 4) return `${raw.slice(0, 4)}-${raw.slice(4, 8)}`
  return raw
})

function onInput(e: Event) {
  const val = (e.target as HTMLInputElement).value
  const raw = val.replace(/[^a-zA-Z0-9]/g, '').toUpperCase().slice(0, 8)
  userCode.value = raw.length > 4 ? `${raw.slice(0, 4)}-${raw.slice(4)}` : raw
}

async function approve() {
  if (formattedCode.value.length < 9) return
  loading.value = true
  try {
    await api('/oauth/device/approve', {
      method: 'POST',
      body: { user_code: formattedCode.value },
    })
    done.value = 'approved'
    toast.add({ title: 'Zatwierdzone', description: 'Urządzenie zostało autoryzowane.', color: 'green' })
  } catch {
    toast.add({ title: 'Błąd', description: 'Nieprawidłowy lub wygasły kod.', color: 'red' })
  } finally {
    loading.value = false
  }
}

async function deny() {
  if (formattedCode.value.length < 9) return
  loading.value = true
  try {
    await api('/oauth/device/deny', {
      method: 'POST',
      body: { user_code: formattedCode.value },
    })
    done.value = 'denied'
    toast.add({ title: 'Odrzucone', description: 'Żądanie zostało odrzucone.', color: 'orange' })
  } catch {
    toast.add({ title: 'Błąd', description: 'Nieprawidłowy lub wygasły kod.', color: 'red' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-background-black flex items-center justify-center p-4">
    <div class="bg-card-black border border-border-gray rounded-xl p-8 w-full max-w-md">

      <div v-if="done === 'approved'" class="text-center space-y-4">
        <UIcon name="i-heroicons-check-circle" class="text-electric-green text-6xl mx-auto" />
        <p class="text-pure-white text-xl font-semibold">Urządzenie autoryzowane</p>
        <p class="text-gray-400 text-sm">Możesz zamknąć tę stronę. Urządzenie zostało połączone z LockIner.</p>
      </div>

      <div v-else-if="done === 'denied'" class="text-center space-y-4">
        <UIcon name="i-heroicons-x-circle" class="text-danger-red text-6xl mx-auto" />
        <p class="text-pure-white text-xl font-semibold">Żądanie odrzucone</p>
        <p class="text-gray-400 text-sm">Urządzenie nie zostało autoryzowane.</p>
      </div>

      <div v-else class="space-y-6">
        <div class="text-center space-y-2">
          <UIcon name="i-heroicons-device-phone-mobile" class="text-cyber-blue text-4xl mx-auto" />
          <h1 class="text-pure-white text-2xl font-bold">Autoryzacja urządzenia</h1>
          <p class="text-gray-400 text-sm">Wpisz kod wyświetlony przez urządzenie (np. Byczq)</p>
        </div>

        <div class="space-y-4">
          <UInput
            :value="userCode"
            placeholder="ABCD-1234"
            size="xl"
            class="text-center text-2xl font-mono tracking-widest"
            maxlength="9"
            @input="onInput"
          />
        </div>

        <div class="flex gap-3">
          <UButton
            color="red"
            variant="outline"
            class="flex-1"
            :disabled="formattedCode.length < 9 || loading"
            @click="deny"
          >
            Odrzuć
          </UButton>
          <UButton
            color="green"
            class="flex-1"
            :disabled="formattedCode.length < 9 || loading"
            :loading="loading"
            @click="approve"
          >
            Zatwierdź
          </UButton>
        </div>
      </div>

    </div>
  </div>
</template>
