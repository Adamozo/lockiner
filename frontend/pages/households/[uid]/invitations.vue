<script setup lang="ts">
import { useInvitations } from '~/composables/useInvitations'
import { useHouseholds } from '~/composables/useHouseholds'
import { usePermissions } from '~/composables/usePermissions'

definePageMeta({
  layout: 'default',
})

const route = useRoute()
const toast = useToast()

const householdUid = computed(() => route.params.uid as string)

const { currentHousehold, fetchHousehold, isCurrentUserManager } = useHouseholds()
const { isBlocked, canInviteToCurrentHousehold, canManageCurrentHousehold } = usePermissions()
const {
  invitations,
  loading,
  error,
  createInvitation,
  listInvitations,
  revokeInvitation,
  getInvitationLink,
  copyInvitationLink,
} = useInvitations()

// Create invitation form
const showCreateDialog = ref(false)
const createForm = ref({
  expiresInDays: 7,
  maxUses: null as number | null,
})

// Revoke confirmation
const showRevokeDialog = ref(false)
const invitationToRevoke = ref<{ id: number; token: string } | null>(null)

// Fetch data on mount
onMounted(async () => {
  await fetchHousehold(householdUid.value)
  await listInvitations(householdUid.value)
})

// Update SEO
watchEffect(() => {
  if (currentHousehold.value) {
    useSeoMeta({
      title: `Invitations - ${currentHousehold.value.name} - LockIner`,
      description: 'Manage household invitations',
    })
  }
})

// Format date
const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return 'Never'
  return new Date(dateStr).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Handle create invitation
const handleCreate = async () => {
  try {
    const invitation = await createInvitation(householdUid.value, {
      expires_in_days: createForm.value.expiresInDays || null,
      max_uses: createForm.value.maxUses || null,
    })

    toast.add({
      title: 'Invitation created',
      description: 'Copy the link to share with others',
      color: 'green',
    })

    showCreateDialog.value = false

    // Reset form
    createForm.value = {
      expiresInDays: 7,
      maxUses: null,
    }
  } catch {
    toast.add({
      title: 'Error',
      description: error.value || 'Failed to create invitation',
      color: 'red',
    })
  }
}

// Handle copy link
const handleCopy = async (token: string) => {
  const success = await copyInvitationLink(token)

  if (success) {
    toast.add({
      title: 'Copied!',
      description: 'Invitation link copied to clipboard',
      color: 'green',
    })
  } else {
    toast.add({
      title: 'Error',
      description: 'Failed to copy to clipboard',
      color: 'red',
    })
  }
}

// Confirm revoke
const confirmRevoke = (invitation: { id: number; token: string }) => {
  invitationToRevoke.value = invitation
  showRevokeDialog.value = true
}

// Handle revoke
const handleRevoke = async () => {
  if (!invitationToRevoke.value) return

  try {
    await revokeInvitation(householdUid.value, invitationToRevoke.value.id)

    toast.add({
      title: 'Revoked',
      description: 'Invitation has been revoked',
      color: 'green',
    })

    showRevokeDialog.value = false
    invitationToRevoke.value = null
  } catch {
    toast.add({
      title: 'Error',
      description: error.value || 'Failed to revoke invitation',
      color: 'red',
    })
  }
}

// Check if invitation is expired
const isExpired = (expiresAt: string | null): boolean => {
  if (!expiresAt) return false
  return new Date(expiresAt) < new Date()
}

// Check if invitation is exhausted
const isExhausted = (inv: { max_uses: number | null; uses_count: number }): boolean => {
  if (!inv.max_uses) return false
  return inv.uses_count >= inv.max_uses
}
</script>

<template>
  <div class="space-y-8">
    <!-- Access denied for non-managers -->
    <CommonAccessDenied
      v-if="currentHousehold && !canManageCurrentHousehold"
      type="not_household_manager"
      message="Only household managers can manage invitations"
      :show-back-button="true"
      :show-home-button="false"
    />

    <template v-else>
    <!-- Header -->
    <header>
      <NuxtLink
        :to="`/households/${householdUid}`"
        class="inline-flex items-center gap-2 text-pure-white/60 hover:text-pure-white transition-colors mb-4"
      >
        <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        <span>Back to {{ currentHousehold?.name || 'Household' }}</span>
      </NuxtLink>

      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-pure-white">Invitations</h1>
          <p class="mt-2 text-pure-white/60">
            Manage invitation links for {{ currentHousehold?.name }}
          </p>
        </div>

        <BaseButton
          v-if="isCurrentUserManager"
          variant="primary"
          icon="i-heroicons-plus"
          @click="showCreateDialog = true"
        >
          Create Invitation
        </BaseButton>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="loading && invitations.length === 0" class="flex justify-center py-12">
      <div class="w-8 h-8 border-2 border-cyber-blue border-t-transparent rounded-full animate-spin" />
    </div>

    <!-- Error -->
    <div
      v-else-if="error && invitations.length === 0"
      class="p-6 bg-danger-red/10 border border-danger-red/30 rounded-lg"
    >
      <div class="flex items-center gap-3 text-danger-red">
        <UIcon name="i-heroicons-exclamation-circle" class="w-6 h-6" />
        <span>{{ error }}</span>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="invitations.length === 0"
      class="text-center py-16"
    >
      <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-card-black border border-border-gray flex items-center justify-center">
        <UIcon name="i-heroicons-envelope" class="w-10 h-10 text-pure-white/40" />
      </div>
      <h2 class="text-xl font-semibold text-pure-white mb-2">No active invitations</h2>
      <p class="text-pure-white/60 mb-6 max-w-md mx-auto">
        Create an invitation link to invite people to join this household.
      </p>
      <BaseButton
        v-if="isCurrentUserManager"
        variant="primary"
        icon="i-heroicons-plus"
        @click="showCreateDialog = true"
      >
        Create First Invitation
      </BaseButton>
    </div>

    <!-- Invitations list -->
    <div v-else class="space-y-4">
      <div
        v-for="invitation in invitations"
        :key="invitation.id"
        class="bg-card-black border border-border-gray rounded-lg p-6"
        :class="{
          'opacity-50': !invitation.is_active || isExpired(invitation.expires_at) || isExhausted(invitation),
        }"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <!-- Token/Link -->
            <div class="flex items-center gap-2 mb-3">
              <code class="px-3 py-1.5 bg-background-black border border-border-gray rounded text-sm text-pure-white/80 font-mono truncate max-w-md">
                {{ getInvitationLink(invitation.token) }}
              </code>
              <button
                class="p-2 text-pure-white/60 hover:text-cyber-blue transition-colors"
                @click="handleCopy(invitation.token)"
              >
                <UIcon name="i-heroicons-clipboard-document" class="w-5 h-5" />
              </button>
            </div>

            <!-- Stats -->
            <div class="flex flex-wrap gap-4 text-sm">
              <div>
                <span class="text-pure-white/40">Uses:</span>
                <span class="text-pure-white ml-1">
                  {{ invitation.uses_count }}{{ invitation.max_uses ? ` / ${invitation.max_uses}` : '' }}
                </span>
              </div>
              <div>
                <span class="text-pure-white/40">Expires:</span>
                <span class="text-pure-white ml-1">{{ formatDate(invitation.expires_at) }}</span>
              </div>
              <div>
                <span class="text-pure-white/40">Created:</span>
                <span class="text-pure-white ml-1">{{ formatDate(invitation.created_at) }}</span>
              </div>
              <div>
                <span class="text-pure-white/40">By:</span>
                <span class="text-pure-white ml-1">{{ invitation.created_by_name }}</span>
              </div>
            </div>
          </div>

          <!-- Status & Actions -->
          <div class="flex items-center gap-3">
            <UBadge
              v-if="!invitation.is_active"
              color="error"
              variant="subtle"
            >
              Revoked
            </UBadge>
            <UBadge
              v-else-if="isExpired(invitation.expires_at)"
              color="warning"
              variant="subtle"
            >
              Expired
            </UBadge>
            <UBadge
              v-else-if="isExhausted(invitation)"
              color="neutral"
              variant="subtle"
            >
              Exhausted
            </UBadge>
            <UBadge
              v-else
              color="success"
              variant="subtle"
            >
              Active
            </UBadge>

            <BaseButton
              v-if="invitation.is_active && isCurrentUserManager"
              variant="danger"
              size="sm"
              icon="i-heroicons-trash"
              @click="confirmRevoke(invitation)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Create invitation dialog -->
    <BaseModal v-model="showCreateDialog" title="Create Invitation" max-width="lg">
      <form @submit.prevent="handleCreate" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">
            Expires in (days)
          </label>
          <input
            v-model.number="createForm.expiresInDays"
            type="number"
            min="1"
            max="365"
            placeholder="7"
            class="w-full px-4 py-2.5 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 focus:border-cyber-blue focus:ring-cyber-blue/30"
          />
          <p class="mt-1 text-sm text-pure-white/40">
            Leave empty for no expiration
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-pure-white mb-2">
            Maximum uses
          </label>
          <input
            v-model.number="createForm.maxUses"
            type="number"
            min="1"
            placeholder="Unlimited"
            class="w-full px-4 py-2.5 border border-border-gray rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 focus:border-cyber-blue focus:ring-cyber-blue/30"
          />
          <p class="mt-1 text-sm text-pure-white/40">
            Leave empty for unlimited uses
          </p>
        </div>

        <div class="flex justify-end gap-2 pt-4">
          <BaseButton
            type="button"
            variant="secondary"
            @click="showCreateDialog = false"
          >
            Cancel
          </BaseButton>
          <BaseButton
            type="submit"
            variant="primary"
            :loading="loading"
          >
            Create Invitation
          </BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Revoke confirmation dialog -->
    <BaseModal v-model="showRevokeDialog" title="Revoke Invitation" max-width="lg">
      <div class="space-y-4">
        <p class="text-pure-white/80">
          Are you sure you want to revoke this invitation? Anyone with the link will no longer be able to join.
        </p>

        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="showRevokeDialog = false">
            Cancel
          </BaseButton>
          <BaseButton variant="danger" :loading="loading" @click="handleRevoke">
            Revoke
          </BaseButton>
        </div>
      </div>
    </BaseModal>
    </template>
  </div>
</template>
