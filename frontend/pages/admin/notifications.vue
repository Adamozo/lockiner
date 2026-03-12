<script setup lang="ts">
definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Admin — Powiadomienia - LockIner' })

const admin = useAdmin()
const toast = useToast()

const title = ref('')
const body = ref('')
const type = ref('general')
const target = ref<'all' | 'selected'>('all')
const userIds = ref('')
const sending = ref(false)

const handleSend = async () => {
  if (!title.value.trim() || !body.value.trim()) {
    toast.add({ title: 'Błąd', description: 'Tytuł i treść są wymagane', color: 'red' })
    return
  }
  sending.value = true
  try {
    const ids = target.value === 'selected'
      ? userIds.value.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n))
      : []

    const result = await admin.sendNotification({
      title: title.value,
      body: body.value,
      notification_type: type.value,
      target: target.value,
      user_ids: ids,
    })

    toast.add({
      title: 'Wysłano',
      description: `Dostarczono do ${(result as { recipients_count: number }).recipients_count} użytkowników`,
      color: 'green',
    })

    title.value = ''
    body.value = ''
    type.value = 'general'
    target.value = 'all'
    userIds.value = ''
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się wysłać powiadomienia', color: 'red' })
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold text-pure-white flex items-center gap-3">
        <UIcon name="i-heroicons-bell" class="w-7 h-7 text-warning-orange" />
        Powiadomienia masowe
      </h1>
      <p class="mt-1 text-pure-white/50 text-sm">Wyślij powiadomienie push do użytkowników</p>
    </header>

    <div class="max-w-2xl bg-card-black border border-border-gray rounded-xl p-6 space-y-5">

      <div>
        <label class="block text-xs text-pure-white/40 mb-1.5 uppercase tracking-wider">Tytuł</label>
        <input
          v-model="title"
          type="text"
          placeholder="Tytuł powiadomienia..."
          class="w-full px-3 py-2.5 bg-background-black border border-border-gray rounded-lg text-pure-white placeholder-pure-white/20 focus:outline-none focus:border-warning-orange"
        />
      </div>

      <div>
        <label class="block text-xs text-pure-white/40 mb-1.5 uppercase tracking-wider">Treść</label>
        <textarea
          v-model="body"
          rows="4"
          placeholder="Treść powiadomienia..."
          class="w-full px-3 py-2.5 bg-background-black border border-border-gray rounded-lg text-pure-white placeholder-pure-white/20 focus:outline-none focus:border-warning-orange resize-none"
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-pure-white/40 mb-1.5 uppercase tracking-wider">Typ</label>
          <select
            v-model="type"
            class="w-full px-3 py-2.5 bg-background-black border border-border-gray rounded-lg text-pure-white focus:outline-none focus:border-warning-orange"
          >
            <option value="general">General</option>
            <option value="system">System</option>
            <option value="alert">Alert</option>
          </select>
        </div>

        <div>
          <label class="block text-xs text-pure-white/40 mb-1.5 uppercase tracking-wider">Odbiorcy</label>
          <div class="flex gap-4 pt-2">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="target" type="radio" value="all" class="accent-warning-orange" />
              <span class="text-sm text-pure-white/80">Wszyscy</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="target" type="radio" value="selected" class="accent-warning-orange" />
              <span class="text-sm text-pure-white/80">Wybrani</span>
            </label>
          </div>
        </div>
      </div>

      <div v-if="target === 'selected'">
        <label class="block text-xs text-pure-white/40 mb-1.5 uppercase tracking-wider">ID użytkowników (przecinek)</label>
        <input
          v-model="userIds"
          type="text"
          placeholder="1, 2, 3"
          class="w-full px-3 py-2.5 bg-background-black border border-border-gray rounded-lg text-pure-white placeholder-pure-white/20 focus:outline-none focus:border-warning-orange"
        />
      </div>

      <button
        @click="handleSend"
        :disabled="sending || !title.trim() || !body.trim()"
        class="w-full px-5 py-3 bg-warning-orange/10 border border-warning-orange/30 rounded-lg text-warning-orange hover:bg-warning-orange/20 transition-colors disabled:opacity-40 font-medium flex items-center justify-center gap-2"
      >
        <UIcon v-if="!sending" name="i-heroicons-paper-airplane" class="w-4 h-4" />
        <div v-else class="w-4 h-4 border-2 border-warning-orange border-t-transparent rounded-full animate-spin" />
        {{ sending ? 'Wysyłam...' : 'Wyślij powiadomienie' }}
      </button>
    </div>
  </div>
</template>
