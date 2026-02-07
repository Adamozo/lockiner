<script setup lang="ts">
import type { VoucherAdmin, UserAdmin } from '~/types/api'

definePageMeta({
  layout: 'default',
})

useSeoMeta({
  title: 'Admin Panel - LockIner',
  description: 'Administration panel',
})

const admin = useAdmin()
const toast = useToast()

// Tab state
const activeTab = ref<'vouchers' | 'users' | 'notifications'>('vouchers')

// ========================================================================
// Vouchers
// ========================================================================
const vouchers = ref<VoucherAdmin[]>([])
const vouchersLoading = ref(false)
const generateCount = ref(5)
const generating = ref(false)

const loadVouchers = async () => {
  vouchersLoading.value = true
  try {
    vouchers.value = await admin.fetchVouchers()
  } catch {
    toast.add({ title: 'Error', description: 'Failed to load vouchers', color: 'red' })
  } finally {
    vouchersLoading.value = false
  }
}

const handleGenerate = async () => {
  generating.value = true
  try {
    const result = await admin.generateVouchers(generateCount.value)
    toast.add({ title: 'Success', description: `Generated ${result.count} vouchers`, color: 'green' })
    await loadVouchers()
  } catch {
    toast.add({ title: 'Error', description: 'Failed to generate vouchers', color: 'red' })
  } finally {
    generating.value = false
  }
}

const handleBlockVoucher = async (id: number) => {
  try {
    await admin.blockVoucher(id)
    await loadVouchers()
    toast.add({ title: 'Voucher blocked', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to block voucher', color: 'red' })
  }
}

const handleUnblockVoucher = async (id: number) => {
  try {
    await admin.unblockVoucher(id)
    await loadVouchers()
    toast.add({ title: 'Voucher unblocked', color: 'green' })
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    toast.add({ title: 'Error', description: err.data?.detail || 'Failed to unblock voucher', color: 'red' })
  }
}

// ========================================================================
// Users
// ========================================================================
const users = ref<UserAdmin[]>([])
const usersLoading = ref(false)

const loadUsers = async () => {
  usersLoading.value = true
  try {
    users.value = await admin.fetchUsers()
  } catch {
    toast.add({ title: 'Error', description: 'Failed to load users', color: 'red' })
  } finally {
    usersLoading.value = false
  }
}

const handleBlockUser = async (id: number) => {
  try {
    await admin.blockUser(id)
    await loadUsers()
    toast.add({ title: 'User blocked', color: 'green' })
  } catch {
    toast.add({ title: 'Error', color: 'red' })
  }
}

const handleUnblockUser = async (id: number) => {
  try {
    await admin.unblockUser(id)
    await loadUsers()
    toast.add({ title: 'User unblocked', color: 'green' })
  } catch {
    toast.add({ title: 'Error', color: 'red' })
  }
}

const handleSetRole = async (id: number, role: 'user' | 'admin') => {
  try {
    await admin.setUserRole(id, role)
    await loadUsers()
    toast.add({ title: `Role changed to ${role}`, color: 'green' })
  } catch {
    toast.add({ title: 'Error', color: 'red' })
  }
}

// ========================================================================
// Notifications
// ========================================================================
const notifTitle = ref('')
const notifBody = ref('')
const notifType = ref('general')
const notifTarget = ref<'all' | 'selected'>('all')
const notifUserIds = ref('')
const sending = ref(false)

const handleSendNotification = async () => {
  if (!notifTitle.value.trim() || !notifBody.value.trim()) {
    toast.add({ title: 'Error', description: 'Title and body are required', color: 'red' })
    return
  }

  sending.value = true
  try {
    const userIds = notifTarget.value === 'selected'
      ? notifUserIds.value.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n))
      : []

    const result = await admin.sendNotification({
      title: notifTitle.value,
      body: notifBody.value,
      notification_type: notifType.value,
      target: notifTarget.value,
      user_ids: userIds,
    })

    toast.add({
      title: 'Notification sent',
      description: `Sent to ${(result as { recipients_count: number }).recipients_count} users`,
      color: 'green',
    })

    // Reset form
    notifTitle.value = ''
    notifBody.value = ''
    notifType.value = 'general'
    notifTarget.value = 'all'
    notifUserIds.value = ''
  } catch {
    toast.add({ title: 'Error', description: 'Failed to send notification', color: 'red' })
  } finally {
    sending.value = false
  }
}

// Load data for active tab
watch(activeTab, (tab) => {
  if (tab === 'vouchers' && vouchers.value.length === 0) loadVouchers()
  if (tab === 'users' && users.value.length === 0) loadUsers()
}, { immediate: true })

const statusColor = (status: string) => {
  switch (status) {
    case 'available': return 'text-electric-green'
    case 'used': return 'text-pure-white/40'
    case 'blocked': return 'text-danger-red'
    default: return 'text-pure-white/60'
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <header>
      <h1 class="text-3xl font-bold text-pure-white flex items-center gap-3">
        <UIcon name="i-heroicons-shield-check" class="w-8 h-8 text-warning-orange" />
        Admin Panel
      </h1>
      <p class="mt-1 text-pure-white/60">Manage vouchers, users, and notifications</p>
    </header>

    <!-- Tabs -->
    <div class="flex gap-2 border-b border-border-gray pb-0">
      <button
        v-for="tab in [
          { key: 'vouchers', label: 'Vouchers', icon: 'i-heroicons-ticket' },
          { key: 'users', label: 'Users', icon: 'i-heroicons-users' },
          { key: 'notifications', label: 'Notifications', icon: 'i-heroicons-bell' },
        ] as const"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 -mb-[1px] transition-colors"
        :class="activeTab === tab.key
          ? 'border-cyber-blue text-cyber-blue'
          : 'border-transparent text-pure-white/50 hover:text-pure-white/80'"
      >
        <UIcon :name="tab.icon" class="w-4 h-4" />
        {{ tab.label }}
      </button>
    </div>

    <!-- ================================================================ -->
    <!-- VOUCHERS TAB -->
    <!-- ================================================================ -->
    <div v-if="activeTab === 'vouchers'" class="space-y-6">
      <!-- Generate -->
      <div class="bg-card-black border border-border-gray rounded-xl p-5">
        <h3 class="text-sm font-semibold text-pure-white/60 uppercase tracking-wider mb-4">Generate Vouchers</h3>
        <div class="flex items-end gap-3">
          <div>
            <label class="block text-xs text-pure-white/40 mb-1">Count</label>
            <input
              v-model.number="generateCount"
              type="number"
              min="1"
              max="100"
              class="w-24 px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white focus:outline-none focus:border-electric-green"
            />
          </div>
          <button
            @click="handleGenerate"
            :disabled="generating"
            class="px-5 py-2 bg-electric-green/10 border border-electric-green/30 rounded-lg text-electric-green hover:bg-electric-green/20 transition-colors disabled:opacity-50"
          >
            {{ generating ? 'Generating...' : 'Generate' }}
          </button>
        </div>
      </div>

      <!-- Voucher List -->
      <div v-if="vouchersLoading" class="text-center py-8">
        <div class="w-6 h-6 border-2 border-cyber-blue border-t-transparent rounded-full animate-spin mx-auto" />
      </div>
      <div v-else class="bg-card-black border border-border-gray rounded-xl overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-border-gray text-left">
                <th class="px-4 py-3 text-xs font-semibold text-pure-white/40 uppercase">Code</th>
                <th class="px-4 py-3 text-xs font-semibold text-pure-white/40 uppercase">Status</th>
                <th class="px-4 py-3 text-xs font-semibold text-pure-white/40 uppercase">Used By</th>
                <th class="px-4 py-3 text-xs font-semibold text-pure-white/40 uppercase">Created</th>
                <th class="px-4 py-3 text-xs font-semibold text-pure-white/40 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="v in vouchers"
                :key="v.id"
                class="border-b border-border-gray/50 hover:bg-background-black/30"
              >
                <td class="px-4 py-3 font-mono text-xs text-pure-white/80">{{ v.code }}</td>
                <td class="px-4 py-3">
                  <span class="text-xs font-semibold uppercase" :class="statusColor(v.status)">{{ v.status }}</span>
                </td>
                <td class="px-4 py-3 text-sm text-pure-white/60">{{ v.used_by_name || '-' }}</td>
                <td class="px-4 py-3 text-xs text-pure-white/40">{{ v.created_at?.slice(0, 10) }}</td>
                <td class="px-4 py-3">
                  <button
                    v-if="v.status === 'available'"
                    @click="handleBlockVoucher(v.id)"
                    class="text-xs px-2 py-1 rounded bg-danger-red/10 text-danger-red hover:bg-danger-red/20 transition-colors"
                  >
                    Block
                  </button>
                  <button
                    v-else-if="v.status === 'blocked'"
                    @click="handleUnblockVoucher(v.id)"
                    class="text-xs px-2 py-1 rounded bg-electric-green/10 text-electric-green hover:bg-electric-green/20 transition-colors"
                  >
                    Unblock
                  </button>
                  <span v-else class="text-xs text-pure-white/20">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="vouchers.length === 0" class="text-center py-8 text-pure-white/40">
          No vouchers yet
        </div>
      </div>
    </div>

    <!-- ================================================================ -->
    <!-- USERS TAB -->
    <!-- ================================================================ -->
    <div v-if="activeTab === 'users'" class="space-y-6">
      <div v-if="usersLoading" class="text-center py-8">
        <div class="w-6 h-6 border-2 border-cyber-blue border-t-transparent rounded-full animate-spin mx-auto" />
      </div>
      <div v-else class="bg-card-black border border-border-gray rounded-xl overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-border-gray text-left">
                <th class="px-4 py-3 text-xs font-semibold text-pure-white/40 uppercase">ID</th>
                <th class="px-4 py-3 text-xs font-semibold text-pure-white/40 uppercase">Name</th>
                <th class="px-4 py-3 text-xs font-semibold text-pure-white/40 uppercase">Role</th>
                <th class="px-4 py-3 text-xs font-semibold text-pure-white/40 uppercase">Active</th>
                <th class="px-4 py-3 text-xs font-semibold text-pure-white/40 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="u in users"
                :key="u.id"
                class="border-b border-border-gray/50 hover:bg-background-black/30"
              >
                <td class="px-4 py-3 text-sm text-pure-white/60">{{ u.id }}</td>
                <td class="px-4 py-3 text-sm text-pure-white">{{ u.name }}</td>
                <td class="px-4 py-3">
                  <span
                    class="text-xs font-semibold uppercase"
                    :class="u.role === 'admin' ? 'text-warning-orange' : 'text-pure-white/50'"
                  >
                    {{ u.role }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <span
                    class="w-2 h-2 rounded-full inline-block"
                    :class="u.is_active ? 'bg-electric-green' : 'bg-danger-red'"
                  />
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <button
                      v-if="u.is_active"
                      @click="handleBlockUser(u.id)"
                      class="text-xs px-2 py-1 rounded bg-danger-red/10 text-danger-red hover:bg-danger-red/20 transition-colors"
                    >
                      Block
                    </button>
                    <button
                      v-else
                      @click="handleUnblockUser(u.id)"
                      class="text-xs px-2 py-1 rounded bg-electric-green/10 text-electric-green hover:bg-electric-green/20 transition-colors"
                    >
                      Unblock
                    </button>
                    <button
                      v-if="u.role === 'user'"
                      @click="handleSetRole(u.id, 'admin')"
                      class="text-xs px-2 py-1 rounded bg-warning-orange/10 text-warning-orange hover:bg-warning-orange/20 transition-colors"
                    >
                      Make Admin
                    </button>
                    <button
                      v-else
                      @click="handleSetRole(u.id, 'user')"
                      class="text-xs px-2 py-1 rounded bg-cyber-blue/10 text-cyber-blue hover:bg-cyber-blue/20 transition-colors"
                    >
                      Make User
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ================================================================ -->
    <!-- NOTIFICATIONS TAB -->
    <!-- ================================================================ -->
    <div v-if="activeTab === 'notifications'" class="space-y-6">
      <div class="bg-card-black border border-border-gray rounded-xl p-6 space-y-5">
        <h3 class="text-sm font-semibold text-pure-white/60 uppercase tracking-wider">Send Notification</h3>

        <!-- Title -->
        <div>
          <label class="block text-xs text-pure-white/40 mb-1">Title</label>
          <input
            v-model="notifTitle"
            type="text"
            placeholder="Notification title..."
            class="w-full px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white placeholder-pure-white/20 focus:outline-none focus:border-electric-green"
          />
        </div>

        <!-- Body -->
        <div>
          <label class="block text-xs text-pure-white/40 mb-1">Body</label>
          <textarea
            v-model="notifBody"
            rows="3"
            placeholder="Notification message..."
            class="w-full px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white placeholder-pure-white/20 focus:outline-none focus:border-electric-green resize-none"
          />
        </div>

        <!-- Type -->
        <div>
          <label class="block text-xs text-pure-white/40 mb-1">Type</label>
          <select
            v-model="notifType"
            class="w-full px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white focus:outline-none focus:border-electric-green"
          >
            <option value="general">General</option>
            <option value="system">System</option>
            <option value="alert">Alert</option>
          </select>
        </div>

        <!-- Target -->
        <div>
          <label class="block text-xs text-pure-white/40 mb-1">Target</label>
          <div class="flex gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="notifTarget" type="radio" value="all" class="accent-electric-green" />
              <span class="text-sm text-pure-white/80">All users</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="notifTarget" type="radio" value="selected" class="accent-electric-green" />
              <span class="text-sm text-pure-white/80">Selected users</span>
            </label>
          </div>
        </div>

        <!-- User IDs (if selected) -->
        <div v-if="notifTarget === 'selected'">
          <label class="block text-xs text-pure-white/40 mb-1">User IDs (comma-separated)</label>
          <input
            v-model="notifUserIds"
            type="text"
            placeholder="1, 2, 3"
            class="w-full px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white placeholder-pure-white/20 focus:outline-none focus:border-electric-green"
          />
        </div>

        <!-- Send -->
        <button
          @click="handleSendNotification"
          :disabled="sending || !notifTitle.trim() || !notifBody.trim()"
          class="w-full px-5 py-2.5 bg-electric-green/10 border border-electric-green/30 rounded-lg text-electric-green hover:bg-electric-green/20 transition-colors disabled:opacity-50 font-medium"
        >
          {{ sending ? 'Sending...' : 'Send Notification' }}
        </button>
      </div>
    </div>
  </div>
</template>
