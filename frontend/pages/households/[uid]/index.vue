<script setup lang="ts">
import { useHouseholds } from '~/composables/useHouseholds'
import { useHouseholdContext } from '~/composables/useHouseholdContext'
import { usePermissions } from '~/composables/usePermissions'
import type { HouseholdMemberUpdate } from '~/types/api'

definePageMeta({
  layout: 'default',
})

const route = useRoute()
const router = useRouter()
const toast = useToast()

const {
  currentHousehold,
  currentMembers,
  loading,
  error,
  fetchHousehold,
  updateHousehold,
  deleteHousehold,
  updateMember,
  removeMember,
  leaveHousehold,
  isCurrentUserManager,
  currentUserMemberInfo,
} = useHouseholds()

const { setHouseholdContext, isHouseholdContext, currentHouseholdId } = useHouseholdContext()
const {
  isBlocked,
  canManageCurrentHousehold,
  canInviteToCurrentHousehold,
  canViewCurrentHouseholdContent,
  canEditMember,
  canRemoveMember,
} = usePermissions()

const householdUid = computed(() => route.params.uid as string)

// Edit mode
const isEditing = ref(false)
const editForm = ref({
  name: '',
  description: '',
  icon: '',
})

// Delete confirmation
const showDeleteDialog = ref(false)

// Member action dialog
const showMemberActionDialog = ref(false)
const selectedMember = ref<{ userId: number; name: string; role: string } | null>(null)

// Available icons
const availableIcons = [
  { key: 'house', label: 'House' },
  { key: 'garden', label: 'Garden Home' },
  { key: 'apartment', label: 'Apartment' },
  { key: 'neighborhood', label: 'Neighborhood' },
  { key: 'castle', label: 'Estate' },
  { key: 'family', label: 'Family' },
  { key: 'group', label: 'Group' },
  { key: 'building', label: 'Building' },
]

// Fetch household on mount
onMounted(async () => {
  await fetchHousehold(householdUid.value)

  // Initialize edit form
  if (currentHousehold.value) {
    editForm.value = {
      name: currentHousehold.value.name,
      description: currentHousehold.value.description || '',
      icon: currentHousehold.value.icon || '',
    }
  }
})

// Update SEO
watchEffect(() => {
  if (currentHousehold.value) {
    useSeoMeta({
      title: `${currentHousehold.value.name} - LockIner`,
      description: currentHousehold.value.description || 'Household details',
    })
  }
})

// Format date
const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// Start editing
const startEditing = () => {
  if (currentHousehold.value) {
    editForm.value = {
      name: currentHousehold.value.name,
      description: currentHousehold.value.description || '',
      icon: currentHousehold.value.icon || '',
    }
  }
  isEditing.value = true
}

// Cancel editing
const cancelEditing = () => {
  isEditing.value = false
}

// Save changes
const saveChanges = async () => {
  if (!editForm.value.name.trim()) {
    toast.add({
      title: 'Error',
      description: 'Name is required',
      color: 'red',
    })
    return
  }

  try {
    await updateHousehold(householdUid.value, {
      name: editForm.value.name.trim(),
      description: editForm.value.description.trim() || null,
      icon: editForm.value.icon || null,
    })

    toast.add({
      title: 'Saved',
      description: 'Household updated successfully',
      color: 'green',
    })

    isEditing.value = false
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to update household',
      color: 'red',
    })
  }
}

// Delete household
const handleDelete = async () => {
  try {
    await deleteHousehold(householdUid.value)

    toast.add({
      title: 'Deleted',
      description: 'Household has been deleted',
      color: 'green',
    })
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to delete household',
      color: 'red',
    })
  }
}

// Select icon
const selectIcon = (icon: string) => {
  editForm.value.icon = editForm.value.icon === icon ? '' : icon
}

// Switch context to this household
const switchToHousehold = () => {
  setHouseholdContext(householdUid.value)
  toast.add({
    title: 'Context switched',
    description: `Now viewing ${currentHousehold.value?.name}`,
    color: 'green',
  })
}

// Switch back to personal
const switchToPersonal = () => {
  setHouseholdContext(null)
  toast.add({
    title: 'Context switched',
    description: 'Now viewing personal finances',
    color: 'green',
  })
}

// Open member action dialog
const openMemberAction = (member: { user_id: number; user_name: string; role: string }) => {
  selectedMember.value = {
    userId: member.user_id,
    name: member.user_name,
    role: member.role,
  }
  showMemberActionDialog.value = true
}

// Change member role
const changeMemberRole = async (newRole: 'manager' | 'member') => {
  if (!selectedMember.value) return

  try {
    await updateMember(householdUid.value, selectedMember.value.userId, { role: newRole })

    toast.add({
      title: 'Updated',
      description: `${selectedMember.value.name} is now a ${newRole}`,
      color: 'green',
    })

    showMemberActionDialog.value = false
    selectedMember.value = null

    // Refresh household
    await fetchHousehold(householdUid.value)
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to update member role',
      color: 'red',
    })
  }
}

// Block/unblock member
const toggleMemberBlock = async () => {
  if (!selectedMember.value) return

  const member = currentMembers.value.find(m => m.user_id === selectedMember.value?.userId)
  if (!member) return

  const newStatus = member.status === 'blocked' ? 'active' : 'blocked'

  try {
    await updateMember(householdUid.value, selectedMember.value.userId, { status: newStatus })

    toast.add({
      title: 'Updated',
      description: `${selectedMember.value.name} has been ${newStatus === 'blocked' ? 'blocked' : 'unblocked'}`,
      color: 'green',
    })

    showMemberActionDialog.value = false
    selectedMember.value = null

    // Refresh household
    await fetchHousehold(householdUid.value)
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to update member status',
      color: 'red',
    })
  }
}

// Remove member
const handleRemoveMember = async () => {
  if (!selectedMember.value) return

  try {
    await removeMember(householdUid.value, selectedMember.value.userId)

    toast.add({
      title: 'Removed',
      description: `${selectedMember.value.name} has been removed`,
      color: 'green',
    })

    showMemberActionDialog.value = false
    selectedMember.value = null

    // Refresh household
    await fetchHousehold(householdUid.value)
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to remove member',
      color: 'red',
    })
  }
}

// Leave household
const handleLeave = async () => {
  try {
    await leaveHousehold(householdUid.value)

    toast.add({
      title: 'Left',
      description: 'You have left the household',
      color: 'green',
    })
  } catch {
    toast.add({
      title: 'Error',
      description: 'Failed to leave household',
      color: 'red',
    })
  }
}

// Get role badge color
const getRoleBadgeColor = (role: string) => {
  return role === 'manager' ? 'primary' : 'neutral'
}

// Get status badge color
const getStatusBadgeColor = (status: string) => {
  return status === 'blocked' ? 'error' : 'success'
}
</script>

<template>
  <div class="space-y-8">
    <!-- Loading -->
    <div v-if="loading && !currentHousehold" class="flex justify-center py-12">
      <div class="w-8 h-8 border-2 border-cyber-blue border-t-transparent rounded-full animate-spin" />
    </div>

    <!-- Error -->
    <div
      v-else-if="error && !currentHousehold"
      class="p-6 bg-danger-red/10 border border-danger-red/30 rounded-lg"
    >
      <div class="flex items-center gap-3 text-danger-red">
        <UIcon name="i-heroicons-exclamation-circle" class="w-6 h-6 flex-shrink-0" />
        <span>{{ error }}</span>
      </div>
      <NuxtLink to="/households" class="mt-4 inline-block">
        <BaseButton variant="secondary">Back to Households</BaseButton>
      </NuxtLink>
    </div>

    <!-- Blocked access -->
    <CommonBlockedAccess
      v-else-if="currentHousehold && isBlocked"
      :household-name="currentHousehold.name"
    >
      <template #actions>
        <BaseButton
          variant="danger"
          class="w-full"
          icon="i-heroicons-arrow-right-on-rectangle"
          @click="handleLeave"
        >
          Leave Household
        </BaseButton>
      </template>
    </CommonBlockedAccess>

    <!-- Content -->
    <template v-else-if="currentHousehold && !isBlocked">
      <!-- Header -->
      <header class="space-y-4">
        <NuxtLink
          to="/households"
          class="inline-flex items-center gap-2 text-pure-white/60 hover:text-pure-white transition-colors"
        >
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
          <span>Back to Households</span>
        </NuxtLink>

        <div class="flex items-center gap-4">
          <div class="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-cyber-blue/10 border border-cyber-blue/30 flex items-center justify-center flex-shrink-0">
            <HouseholdIcon
              :icon="currentHousehold.icon || 'house'"
              :size="28"
              color="#00D4FF"
            />
          </div>
          <div class="min-w-0 flex-1">
            <h1 class="text-xl sm:text-2xl md:text-3xl font-bold text-pure-white truncate">{{ currentHousehold.name }}</h1>
            <p v-if="currentHousehold.description" class="mt-1 text-sm text-pure-white/60 line-clamp-2">
              {{ currentHousehold.description }}
            </p>
          </div>
        </div>

        <!-- Action buttons - responsive grid -->
        <div class="flex flex-wrap gap-2">
          <!-- Analytics link -->
          <NuxtLink :to="`/households/${householdUid}/analytics`">
            <BaseButton
              variant="secondary"
              icon="i-heroicons-chart-bar"
              size="sm"
            >
              Analytics
            </BaseButton>
          </NuxtLink>

          <!-- Context switcher -->
          <BaseButton
            v-if="currentHouseholdId === householdUid"
            variant="secondary"
            icon="i-heroicons-user"
            size="sm"
            @click="switchToPersonal"
          >
            Personal
          </BaseButton>
          <BaseButton
            v-else
            variant="primary"
            icon="i-heroicons-home"
            size="sm"
            @click="switchToHousehold"
          >
            Household
          </BaseButton>

          <!-- Edit button (manager only) -->
          <BaseButton
            v-if="isCurrentUserManager && !isEditing"
            variant="secondary"
            icon="i-heroicons-pencil"
            size="sm"
            @click="startEditing"
          >
            Edit
          </BaseButton>
        </div>
      </header>

      <!-- Edit form -->
      <div v-if="isEditing" class="bg-card-black border border-border-gray rounded-lg p-6">
        <h2 class="text-lg font-semibold text-pure-white mb-4">Edit Household</h2>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Name</label>
            <input
              v-model="editForm.name"
              type="text"
              class="w-full px-4 py-2.5 border border-border-gray rounded-lg bg-background-black text-pure-white focus:outline-none focus:ring-2 focus:border-cyber-blue focus:ring-cyber-blue/30"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Description</label>
            <textarea
              v-model="editForm.description"
              rows="3"
              class="w-full px-4 py-2.5 border border-border-gray rounded-lg bg-background-black text-pure-white focus:outline-none focus:ring-2 focus:border-cyber-blue focus:ring-cyber-blue/30 resize-none"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-pure-white mb-2">Icon</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="icon in availableIcons"
                :key="icon.key"
                type="button"
                class="w-10 h-10 rounded-lg border flex items-center justify-center transition-all"
                :class="editForm.icon === icon.key
                  ? 'border-cyber-blue bg-cyber-blue/10'
                  : 'border-border-gray hover:border-cyber-blue/50 bg-background-black'"
                :title="icon.label"
                @click="selectIcon(icon.key)"
              >
                <HouseholdIcon
                  :icon="icon.key"
                  :size="20"
                  :color="editForm.icon === icon.key ? '#00D4FF' : '#FFFFFF99'"
                />
              </button>
            </div>
          </div>

          <div class="flex items-center gap-2 pt-2">
            <BaseButton variant="primary" @click="saveChanges" :loading="loading">
              Save Changes
            </BaseButton>
            <BaseButton variant="secondary" @click="cancelEditing">
              Cancel
            </BaseButton>
          </div>
        </div>
      </div>

      <!-- Members section -->
      <div class="bg-card-black border border-border-gray rounded-lg overflow-hidden">
        <div class="px-6 py-4 border-b border-border-gray flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-pure-white">Members</h2>
            <p class="text-sm text-pure-white/60">{{ currentMembers.length }} member(s)</p>
          </div>

          <NuxtLink v-if="isCurrentUserManager" :to="`/households/${householdUid}/invitations`">
            <BaseButton variant="primary" icon="i-heroicons-user-plus" size="sm">
              Invite
            </BaseButton>
          </NuxtLink>
        </div>

        <div class="divide-y divide-border-gray">
          <div
            v-for="member in currentMembers"
            :key="member.user_id"
            class="px-6 py-4 flex items-center justify-between"
          >
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full bg-gradient-to-br from-cyber-blue to-electric-green flex items-center justify-center text-sm font-bold text-background-black">
                {{ member.user_name.charAt(0).toUpperCase() }}
              </div>
              <div>
                <p class="font-medium text-pure-white">
                  {{ member.user_name }}
                  <span v-if="member.user_id === currentUserMemberInfo?.user_id" class="text-pure-white/40">(you)</span>
                </p>
                <p class="text-sm text-pure-white/60">{{ member.user_email }}</p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <UBadge :color="getRoleBadgeColor(member.role)" variant="subtle">
                {{ member.role }}
              </UBadge>
              <UBadge v-if="member.status === 'blocked'" color="error" variant="subtle">
                blocked
              </UBadge>

              <!-- Member actions (manager only, not for self) -->
              <button
                v-if="isCurrentUserManager && member.user_id !== currentUserMemberInfo?.user_id"
                class="p-1 text-pure-white/40 hover:text-pure-white transition-colors"
                @click="openMemberAction(member)"
              >
                <UIcon name="i-heroicons-ellipsis-vertical" class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions section -->
      <div class="flex items-center gap-4">
        <!-- Leave (not for managers if only manager) -->
        <BaseButton
          v-if="currentUserMemberInfo"
          variant="secondary"
          icon="i-heroicons-arrow-right-on-rectangle"
          size="sm"
          @click="handleLeave"
        >
          Leave Household
        </BaseButton>

        <!-- Delete (manager only) -->
        <BaseButton
          v-if="isCurrentUserManager"
          variant="danger"
          icon="i-heroicons-trash"
          size="sm"
          @click="showDeleteDialog = true"
        >
          Delete Household
        </BaseButton>
      </div>

      <!-- Info -->
      <div class="text-sm text-pure-white/40">
        <p>Created {{ formatDate(currentHousehold.created_at) }}</p>
        <p v-if="currentHousehold.updated_at">
          Last updated {{ formatDate(currentHousehold.updated_at) }}
        </p>
      </div>
    </template>

    <!-- Delete confirmation dialog -->
    <BaseModal v-model="showDeleteDialog" title="Delete Household" max-width="lg">
      <div class="space-y-4">
        <p class="text-pure-white/80">
          Are you sure you want to delete <strong>{{ currentHousehold?.name }}</strong>?
          This action cannot be undone. All associated data will be permanently deleted.
        </p>

        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="showDeleteDialog = false">
            Cancel
          </BaseButton>
          <BaseButton variant="danger" @click="handleDelete" :loading="loading">
            Delete
          </BaseButton>
        </div>
      </div>
    </BaseModal>

    <!-- Member action dialog -->
    <BaseModal v-model="showMemberActionDialog" :title="`Manage ${selectedMember?.name}`" max-width="lg">
      <div v-if="selectedMember" class="space-y-4">
        <!-- Role change -->
        <div>
          <p class="text-sm font-medium text-pure-white mb-2">Change Role</p>
          <div class="flex gap-2">
            <BaseButton
              :variant="selectedMember.role === 'manager' ? 'primary' : 'secondary'"
              size="sm"
              @click="changeMemberRole('manager')"
            >
              Manager
            </BaseButton>
            <BaseButton
              :variant="selectedMember.role === 'member' ? 'primary' : 'secondary'"
              size="sm"
              @click="changeMemberRole('member')"
            >
              Member
            </BaseButton>
          </div>
        </div>

        <!-- Block/Unblock -->
        <div>
          <p class="text-sm font-medium text-pure-white mb-2">Access</p>
          <BaseButton
            :variant="currentMembers.find(m => m.user_id === selectedMember.userId)?.status === 'blocked' ? 'primary' : 'secondary'"
            size="sm"
            @click="toggleMemberBlock"
          >
            {{ currentMembers.find(m => m.user_id === selectedMember.userId)?.status === 'blocked' ? 'Unblock' : 'Block' }}
          </BaseButton>
        </div>

        <!-- Remove -->
        <div class="pt-4 border-t border-border-gray">
          <BaseButton
            variant="danger"
            size="sm"
            icon="i-heroicons-trash"
            @click="handleRemoveMember"
          >
            Remove from Household
          </BaseButton>
        </div>

        <div class="flex justify-end pt-2">
          <BaseButton variant="secondary" @click="showMemberActionDialog = false">
            Close
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>
