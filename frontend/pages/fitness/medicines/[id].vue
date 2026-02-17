<script setup lang="ts">
import type { Medicine, MedicineUpdate, MedicineSchedule, MedicineScheduleCreate, MedicineLog } from '~/types/medicine'

definePageMeta({
  layout: 'fitness',
})

const route = useRoute()
const toast = useToast()
const medicineId = computed(() => Number(route.params.id))

const { fetchMedicine, updateMedicine, deleteMedicine, addSchedule, updateSchedule, deleteSchedule } = useMedicines()
const api = useApi()

const medicine = ref<Medicine | null>(null)
const logs = ref<MedicineLog[]>([])
const loading = ref(true)
const isEditing = ref(false)
const showScheduleForm = ref(false)
const editingSchedule = ref<MedicineSchedule | null>(null)

useSeoMeta({
  title: computed(() => medicine.value ? `${medicine.value.name} - Medicines` : 'Medicine - LockIner'),
})

onMounted(async () => {
  try {
    medicine.value = await fetchMedicine(medicineId.value)
    // Fetch logs
    const data = await api<MedicineLog[]>(`/api/v1/fitness/medicines/${medicineId.value}/logs`)
      .catch(() => [] as MedicineLog[])
    logs.value = Array.isArray(data) ? data : []
  } catch {
    toast.add({ title: 'Error', description: 'Medicine not found', color: 'red' })
    navigateTo('/fitness/medicines')
  } finally {
    loading.value = false
  }
})

const handleSaveEdit = async (data: MedicineUpdate) => {
  try {
    medicine.value = await updateMedicine(medicineId.value, data)
    isEditing.value = false
    toast.add({ title: 'Updated', description: 'Medicine updated', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to update', color: 'red' })
  }
}

const handleDelete = async () => {
  if (!confirm(`Delete "${medicine.value?.name}"? This cannot be undone.`)) return
  try {
    await deleteMedicine(medicineId.value)
    toast.add({ title: 'Deleted', color: 'green' })
    navigateTo('/fitness/medicines')
  } catch {
    toast.add({ title: 'Error', description: 'Failed to delete', color: 'red' })
  }
}

const handleAddSchedule = () => {
  editingSchedule.value = null
  showScheduleForm.value = true
}

const handleEditSchedule = (schedule: MedicineSchedule) => {
  editingSchedule.value = schedule
  showScheduleForm.value = true
}

const handleSaveSchedule = async (data: MedicineScheduleCreate) => {
  try {
    if (editingSchedule.value) {
      await updateSchedule(editingSchedule.value.id, data)
    } else {
      await addSchedule(medicineId.value, data)
    }
    // Refresh medicine
    medicine.value = await fetchMedicine(medicineId.value)
    showScheduleForm.value = false
    editingSchedule.value = null
    toast.add({ title: 'Schedule saved', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to save schedule', color: 'red' })
  }
}

const handleDeleteSchedule = async (scheduleId: number) => {
  if (!confirm('Delete this schedule?')) return
  try {
    await deleteSchedule(scheduleId)
    medicine.value = await fetchMedicine(medicineId.value)
    toast.add({ title: 'Schedule deleted', color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to delete schedule', color: 'red' })
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Back link -->
    <NuxtLink
      to="/fitness/medicines"
      class="inline-flex items-center gap-1 text-sm text-pure-white/60 hover:text-pure-white transition-colors"
    >
      <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
      Back to Medicines
    </NuxtLink>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-cyber-blue animate-spin" />
    </div>

    <template v-else-if="medicine">
      <!-- Header -->
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-center gap-3">
          <span
            v-if="medicine.color"
            class="w-4 h-4 rounded-full flex-shrink-0"
            :style="{ backgroundColor: medicine.color }"
          />
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">{{ medicine.name }}</h1>
            <p v-if="medicine.dosage" class="text-pure-white/60 mt-1">
              {{ medicine.dosage }}{{ medicine.unit ? ` ${medicine.unit}` : '' }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <BaseButton
            v-if="!isEditing"
            variant="secondary"
            size="sm"
            icon="i-heroicons-pencil"
            @click="isEditing = true"
          >
            Edit
          </BaseButton>
          <BaseButton
            variant="danger"
            size="sm"
            icon="i-heroicons-trash"
            @click="handleDelete"
          />
        </div>
      </div>

      <!-- Edit Form -->
      <div v-if="isEditing" class="bg-card-black border border-border-gray rounded-xl p-6">
        <MedicineEditForm
          :medicine="medicine"
          @save="handleSaveEdit"
          @cancel="isEditing = false"
        />
      </div>

      <!-- Description -->
      <div v-if="medicine.description && !isEditing" class="bg-card-black border border-border-gray rounded-xl p-6">
        <h2 class="text-sm font-medium text-pure-white/60 mb-2">Description</h2>
        <p class="text-pure-white">{{ medicine.description }}</p>
      </div>

      <!-- Schedules Section -->
      <div class="bg-card-black border border-border-gray rounded-xl p-6">
        <h2 class="text-lg font-semibold text-pure-white mb-4">Schedules</h2>

        <MedicineScheduleForm
          v-if="showScheduleForm"
          :schedule="editingSchedule"
          @save="handleSaveSchedule"
          @cancel="showScheduleForm = false; editingSchedule = null"
        />

        <MedicineScheduleList
          v-else
          :schedules="medicine.schedules"
          @add="handleAddSchedule"
          @edit="handleEditSchedule"
          @delete="handleDeleteSchedule"
        />
      </div>

      <!-- Log History -->
      <div class="bg-card-black border border-border-gray rounded-xl p-6">
        <h2 class="text-lg font-semibold text-pure-white mb-4">Log History</h2>
        <MedicineLogHistory :logs="logs" />
      </div>
    </template>
  </div>
</template>
