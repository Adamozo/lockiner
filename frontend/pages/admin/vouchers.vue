<script setup lang="ts">
import type { VoucherAdmin } from '~/types/api'

definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Admin — Vouchers - LockIner' })

const admin = useAdmin()
const toast = useToast()

const vouchers = ref<VoucherAdmin[]>([])
const loading = ref(false)
const generateCount = ref(5)
const generating = ref(false)

const load = async () => {
  loading.value = true
  try {
    vouchers.value = await admin.fetchVouchers()
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się załadować voucherów', color: 'red' })
  } finally {
    loading.value = false
  }
}

const handleGenerate = async () => {
  generating.value = true
  try {
    const result = await admin.generateVouchers(generateCount.value)
    toast.add({ title: 'Wygenerowano', description: `Dodano ${result.count} voucherów`, color: 'green' })
    await load()
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się wygenerować voucherów', color: 'red' })
  } finally {
    generating.value = false
  }
}

const handleBlock = async (id: number) => {
  try {
    await admin.blockVoucher(id)
    await load()
    toast.add({ title: 'Voucher zablokowany', color: 'green' })
  } catch {
    toast.add({ title: 'Błąd', color: 'red' })
  }
}

const handleUnblock = async (id: number) => {
  try {
    await admin.unblockVoucher(id)
    await load()
    toast.add({ title: 'Voucher odblokowany', color: 'green' })
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.add({ title: 'Błąd', description: err.data?.detail || 'Nie udało się odblokować', color: 'red' })
  }
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text).then(() => {
    toast.add({ title: 'Skopiowano', color: 'green' })
  })
}

const statusColor = (s: string) => ({
  available: 'text-electric-green',
  used: 'text-pure-white/40',
  blocked: 'text-danger-red',
}[s] ?? 'text-pure-white/60')

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold text-pure-white flex items-center gap-3">
        <UIcon name="i-heroicons-ticket" class="w-7 h-7 text-warning-orange" />
        Vouchers
      </h1>
      <p class="mt-1 text-pure-white/50 text-sm">Generuj i zarządzaj kodami dostępu</p>
    </header>

    <!-- Generator -->
    <div class="bg-card-black border border-border-gray rounded-xl p-5">
      <h3 class="text-xs font-semibold text-pure-white/40 uppercase tracking-wider mb-4">Generuj nowe</h3>
      <div class="flex items-end gap-3">
        <div>
          <label class="block text-xs text-pure-white/40 mb-1">Ilość</label>
          <input
            v-model.number="generateCount"
            type="number" min="1" max="100"
            class="w-24 px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white focus:outline-none focus:border-warning-orange"
          />
        </div>
        <button
          @click="handleGenerate"
          :disabled="generating"
          class="px-5 py-2 bg-warning-orange/10 border border-warning-orange/30 rounded-lg text-warning-orange hover:bg-warning-orange/20 transition-colors disabled:opacity-50"
        >
          {{ generating ? 'Generuję...' : 'Generuj' }}
        </button>
      </div>
    </div>

    <!-- Lista -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-6 h-6 border-2 border-warning-orange border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else class="bg-card-black border border-border-gray rounded-xl overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-border-gray">
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">Kod</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">Użyty przez</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">Data</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">Akcje</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="v in vouchers" :key="v.id"
              class="border-b border-border-gray/50 hover:bg-background-black/30"
            >
              <td class="px-4 py-3">
                <div class="flex items-center gap-1.5">
                  <span class="font-mono text-xs text-pure-white/80">{{ v.code.split('-')[0] }}<span class="text-pure-white/30">…</span></span>
                  <button @click="copyToClipboard(v.code)" class="p-1 rounded text-pure-white/30 hover:text-warning-orange hover:bg-warning-orange/10 transition-colors" title="Kopiuj pełny kod">
                    <UIcon name="i-heroicons-clipboard-document" class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
              <td class="px-4 py-3">
                <span class="text-xs font-semibold uppercase" :class="statusColor(v.status)">{{ v.status }}</span>
              </td>
              <td class="px-4 py-3 text-sm text-pure-white/60">{{ v.used_by_name || '—' }}</td>
              <td class="px-4 py-3 text-xs text-pure-white/40">{{ v.created_at?.slice(0, 10) }}</td>
              <td class="px-4 py-3">
                <button v-if="v.status === 'available'" @click="handleBlock(v.id)" class="text-xs px-2 py-1 rounded bg-danger-red/10 text-danger-red hover:bg-danger-red/20 transition-colors">Zablokuj</button>
                <button v-else-if="v.status === 'blocked'" @click="handleUnblock(v.id)" class="text-xs px-2 py-1 rounded bg-electric-green/10 text-electric-green hover:bg-electric-green/20 transition-colors">Odblokuj</button>
                <span v-else class="text-xs text-pure-white/20">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!vouchers.length" class="text-center py-10 text-pure-white/30 text-sm">Brak voucherów</div>
    </div>
  </div>
</template>
