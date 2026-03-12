<script setup lang="ts">
import type { UserAdmin } from '~/types/api'

definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Admin — Users - LockIner' })

const admin = useAdmin()
const toast = useToast()

const users = ref<UserAdmin[]>([])
const loading = ref(false)

const load = async () => {
  loading.value = true
  try {
    users.value = await admin.fetchUsers()
  } catch {
    toast.add({ title: 'Błąd', description: 'Nie udało się załadować użytkowników', color: 'red' })
  } finally {
    loading.value = false
  }
}

const handleBlock = async (id: number) => {
  try { await admin.blockUser(id); await load(); toast.add({ title: 'Zablokowano', color: 'green' }) }
  catch { toast.add({ title: 'Błąd', color: 'red' }) }
}

const handleUnblock = async (id: number) => {
  try { await admin.unblockUser(id); await load(); toast.add({ title: 'Odblokowano', color: 'green' }) }
  catch { toast.add({ title: 'Błąd', color: 'red' }) }
}

const handleSetRole = async (id: number, role: 'user' | 'admin') => {
  try { await admin.setUserRole(id, role); await load(); toast.add({ title: `Rola zmieniona na ${role}`, color: 'green' }) }
  catch { toast.add({ title: 'Błąd', color: 'red' }) }
}

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold text-pure-white flex items-center gap-3">
        <UIcon name="i-heroicons-users" class="w-7 h-7 text-warning-orange" />
        Użytkownicy
      </h1>
      <p class="mt-1 text-pure-white/50 text-sm">Zarządzaj kontami i rolami</p>
    </header>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-6 h-6 border-2 border-warning-orange border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else class="bg-card-black border border-border-gray rounded-xl overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-border-gray">
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">ID</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">Nazwa</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">Rola</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">Aktywny</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">Dołączył</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-pure-white/40 uppercase">Akcje</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="u in users" :key="u.id"
              class="border-b border-border-gray/50 hover:bg-background-black/30"
            >
              <td class="px-4 py-3 text-sm text-pure-white/40">{{ u.id }}</td>
              <td class="px-4 py-3 text-sm text-pure-white font-medium">{{ u.name }}</td>
              <td class="px-4 py-3">
                <span class="text-xs font-semibold uppercase" :class="u.role === 'admin' ? 'text-warning-orange' : 'text-pure-white/50'">
                  {{ u.role }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span class="w-2 h-2 rounded-full inline-block" :class="u.is_active ? 'bg-electric-green' : 'bg-danger-red'" />
              </td>
              <td class="px-4 py-3 text-xs text-pure-white/40">{{ u.created_at?.slice(0, 10) }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <button v-if="u.is_active" @click="handleBlock(u.id)" class="text-xs px-2 py-1 rounded bg-danger-red/10 text-danger-red hover:bg-danger-red/20 transition-colors">Zablokuj</button>
                  <button v-else @click="handleUnblock(u.id)" class="text-xs px-2 py-1 rounded bg-electric-green/10 text-electric-green hover:bg-electric-green/20 transition-colors">Odblokuj</button>
                  <button v-if="u.role === 'user'" @click="handleSetRole(u.id, 'admin')" class="text-xs px-2 py-1 rounded bg-warning-orange/10 text-warning-orange hover:bg-warning-orange/20 transition-colors">→ Admin</button>
                  <button v-else @click="handleSetRole(u.id, 'user')" class="text-xs px-2 py-1 rounded bg-cyber-blue/10 text-cyber-blue hover:bg-cyber-blue/20 transition-colors">→ User</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
