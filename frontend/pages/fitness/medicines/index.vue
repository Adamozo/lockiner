<script setup lang="ts">
import type { Medicine } from '~/types/medicine'

definePageMeta({
  layout: 'fitness',
})

useSeoMeta({
  title: 'Medicines - LockIner',
  description: 'Track your medicines and supplements',
})

const { medicines, todayDoses, loading, fetchMedicines, fetchTodayDoses, deleteMedicine, markDose } = useMedicines()
const toast = useToast()

const showCreateModal = ref(false)

onMounted(async () => {
  await Promise.all([fetchMedicines(), fetchTodayDoses()])
})

const handleToggleDose = async (logId: number, taken: boolean) => {
  try {
    await markDose(logId, taken)
  } catch {
    toast.add({ title: 'Error', description: 'Failed to update dose', color: 'red' })
  }
}

const handleDelete = async (medicine: Medicine) => {
  if (!confirm(`Delete "${medicine.name}"? This will remove all schedules and logs.`)) return
  try {
    await deleteMedicine(medicine.id)
    await fetchTodayDoses()
    toast.add({ title: 'Deleted', description: `${medicine.name} removed`, color: 'green' })
  } catch {
    toast.add({ title: 'Error', description: 'Failed to delete medicine', color: 'red' })
  }
}

const handleCreated = async () => {
  showCreateModal.value = false
  await Promise.all([fetchMedicines(), fetchTodayDoses()])
  toast.add({ title: 'Created', description: 'Medicine added successfully', color: 'green' })
}
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <header class="flex flex-col sm:flex-row items-start sm:items-center sm:justify-between gap-3 sm:gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-pure-white">Medicines</h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-pure-white/60">Track your vitamins, supplements, and medications</p>
      </div>
      <BaseButton
        icon="i-heroicons-plus"
        size="sm"
        variant="primary"
        @click="showCreateModal = true"
      >
        Add Medicine
      </BaseButton>
    </header>

    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-cyber-blue animate-spin" />
    </div>

    <template v-else>
      <!-- Today's Doses Banner -->
      <MedicineTodayBanner
        :doses="todayDoses"
        :loading="false"
        @toggle="handleToggleDose"
      />

      <!-- Medicines Grid -->
      <div v-if="medicines.length > 0">
        <h2 class="text-xl font-semibold text-pure-white mb-4">Your Medicines</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <MedicineCard
            v-for="medicine in medicines"
            :key="medicine.id"
            :medicine="medicine"
            @delete="handleDelete"
          />
        </div>
      </div>

      <!-- Empty state -->
      <div
        v-else
        class="bg-card-black border border-border-gray rounded-lg p-12 text-center"
      >
        <UIcon name="i-heroicons-beaker" class="w-16 h-16 mx-auto text-pure-white/40 mb-4" />
        <h3 class="text-lg font-semibold text-pure-white mb-2">No medicines yet</h3>
        <p class="text-pure-white/60 mb-6">Add your vitamins, supplements, or medications to start tracking</p>
        <BaseButton variant="primary" icon="i-heroicons-plus" @click="showCreateModal = true">
          Add Your First Medicine
        </BaseButton>
      </div>
    </template>

    <!-- Create Modal -->
    <MedicineFormModal
      v-model="showCreateModal"
      @created="handleCreated"
    />
  </div>
</template>
