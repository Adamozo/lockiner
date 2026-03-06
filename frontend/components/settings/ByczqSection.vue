<script setup lang="ts">
const toast = useToast()
const { t } = useI18n()

const loading = ref(false)
const testing = ref(false)

const config = ref({ service_url: '', notify_secret_masked: '', configured: false })
const form = ref({ service_url: '', notify_secret: '' })

const statusColor = computed(() => config.value.configured ? 'text-electric-green' : 'text-pure-white/40')
const statusText = computed(() => config.value.configured ? 'Połączono' : 'Nie skonfigurowano')

async function load() {
  try {
    const data = await $fetch('/api/v1/settings/byczq')
    config.value = data as typeof config.value
    form.value.service_url = config.value.service_url
  } catch {
    // admin only – ignore for non-admins
  }
}

async function save() {
  loading.value = true
  try {
    const body: Record<string, string> = { service_url: form.value.service_url }
    if (form.value.notify_secret) body.notify_secret = form.value.notify_secret
    const data = await $fetch('/api/v1/settings/byczq', { method: 'PUT', body })
    config.value = data as typeof config.value
    form.value.notify_secret = ''
    toast.add({ title: 'Zapisano', description: 'Konfiguracja Byczq zaktualizowana.', color: 'green' })
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się zapisać konfiguracji.', color: 'red' })
  } finally {
    loading.value = false
  }
}

async function testConnection() {
  testing.value = true
  try {
    await $fetch('/api/v1/settings/byczq/test', { method: 'POST' })
    toast.add({ title: 'Połączenie OK', description: 'Byczq odpowiada prawidłowo.', color: 'green' })
  } catch {
    toast.add({ title: 'Brak połączenia', description: 'Nie można się połączyć z Byczq.', color: 'red' })
  } finally {
    testing.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <!-- Status -->
    <div class="p-4 bg-background-black rounded-lg border border-border-gray flex items-center gap-3">
      <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 bg-cyber-blue/10">
        <UIcon name="i-heroicons-cpu-chip" class="w-5 h-5 text-cyber-blue" />
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-pure-white font-medium">Byczq Agent Service</p>
        <p class="text-sm" :class="statusColor">{{ statusText }}</p>
      </div>
      <BaseButton
        v-if="config.configured"
        variant="ghost"
        icon="i-heroicons-signal"
        size="sm"
        :loading="testing"
        @click="testConnection"
      >
        Test
      </BaseButton>
    </div>

    <!-- Form -->
    <div class="space-y-3">
      <div>
        <label class="block text-sm text-pure-white/60 mb-1">URL serwisu Byczq</label>
        <UInput
          v-model="form.service_url"
          placeholder="http://192.168.1.100:8765"
          class="w-full"
        />
        <p class="text-xs text-pure-white/40 mt-1">Adres dostępny z serwera Lockiner (lokalny lub przez tunel)</p>
      </div>

      <div>
        <label class="block text-sm text-pure-white/60 mb-1">
          Notify Secret
          <span v-if="config.notify_secret_masked" class="text-pure-white/40 font-mono ml-1">({{ config.notify_secret_masked }})</span>
        </label>
        <UInput
          v-model="form.notify_secret"
          type="password"
          :placeholder="config.notify_secret_masked ? 'Zostaw puste, aby nie zmieniać' : 'Wpisz tajny klucz...'"
          class="w-full"
        />
        <p class="text-xs text-pure-white/40 mt-1">Ten sam klucz co NOTIFY_SECRET w Jarvis .env</p>
      </div>

      <BaseButton
        variant="primary"
        icon="i-heroicons-check"
        :loading="loading"
        @click="save"
      >
        Zapisz konfigurację
      </BaseButton>
    </div>
  </div>
</template>
