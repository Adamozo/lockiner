import type {
  Medicine,
  MedicineCreate,
  MedicineUpdate,
  MedicineSchedule,
  MedicineScheduleCreate,
  MedicineScheduleUpdate,
  TodayDose,
  MedicineStats,
} from '~/types/medicine'

export function useMedicines() {
  const api = useApi()
  const medicines = ref<Medicine[]>([])
  const todayDoses = ref<TodayDose[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const BASE = '/api/v1/fitness/medicines'

  // --- Medicines ---

  const fetchMedicines = async (): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      medicines.value = await api<Medicine[]>(BASE)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch medicines'
      throw e
    } finally {
      loading.value = false
    }
  }

  const fetchMedicine = async (id: number): Promise<Medicine> => {
    return await api<Medicine>(`${BASE}/${id}`)
  }

  const createMedicine = async (data: MedicineCreate): Promise<Medicine> => {
    loading.value = true
    error.value = null
    try {
      const created = await api<Medicine>(BASE, { method: 'POST', body: data })
      medicines.value.push(created)
      return created
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create medicine'
      throw e
    } finally {
      loading.value = false
    }
  }

  const updateMedicine = async (id: number, data: MedicineUpdate): Promise<Medicine> => {
    loading.value = true
    error.value = null
    try {
      const updated = await api<Medicine>(`${BASE}/${id}`, { method: 'PUT', body: data })
      const index = medicines.value.findIndex(m => m.id === id)
      if (index !== -1) medicines.value[index] = updated
      return updated
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update medicine'
      throw e
    } finally {
      loading.value = false
    }
  }

  const deleteMedicine = async (id: number): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      await api(`${BASE}/${id}`, { method: 'DELETE' })
      medicines.value = medicines.value.filter(m => m.id !== id)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete medicine'
      throw e
    } finally {
      loading.value = false
    }
  }

  // --- Schedules ---

  const addSchedule = async (medicineId: number, data: MedicineScheduleCreate): Promise<MedicineSchedule> => {
    const schedule = await api<MedicineSchedule>(`${BASE}/${medicineId}/schedules`, {
      method: 'POST',
      body: data,
    })
    // Refresh the medicine to get updated schedules
    const updated = await fetchMedicine(medicineId)
    const index = medicines.value.findIndex(m => m.id === medicineId)
    if (index !== -1) medicines.value[index] = updated
    return schedule
  }

  const updateSchedule = async (scheduleId: number, data: MedicineScheduleUpdate): Promise<MedicineSchedule> => {
    return await api<MedicineSchedule>(`${BASE}/schedules/${scheduleId}`, {
      method: 'PUT',
      body: data,
    })
  }

  const deleteSchedule = async (scheduleId: number): Promise<void> => {
    await api(`${BASE}/schedules/${scheduleId}`, { method: 'DELETE' })
  }

  // --- Today's Doses ---

  const fetchTodayDoses = async (): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      todayDoses.value = await api<TodayDose[]>(`${BASE}/today`)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch today doses'
      throw e
    } finally {
      loading.value = false
    }
  }

  const markDose = async (logId: number, taken: boolean): Promise<void> => {
    await api(`${BASE}/logs/${logId}`, {
      method: 'PATCH',
      body: { taken },
    })
    // Update local state
    const dose = todayDoses.value.find(d => d.log_id === logId)
    if (dose) {
      dose.taken = taken
      dose.taken_at = taken ? new Date().toISOString() : null
    }
  }

  // --- Stats ---

  const fetchStats = async (): Promise<MedicineStats> => {
    return await api<MedicineStats>(`${BASE}/stats`)
  }

  // --- Computed ---

  const activeMedicines = computed(() => medicines.value.filter(m => m.active))

  const todayTaken = computed(() => todayDoses.value.filter(d => d.taken).length)

  const todayTotal = computed(() => todayDoses.value.length)

  const todayProgress = computed(() => {
    if (todayTotal.value === 0) return 100
    return Math.round((todayTaken.value / todayTotal.value) * 100)
  })

  return {
    medicines,
    todayDoses,
    loading,
    error,
    activeMedicines,
    todayTaken,
    todayTotal,
    todayProgress,
    fetchMedicines,
    fetchMedicine,
    createMedicine,
    updateMedicine,
    deleteMedicine,
    addSchedule,
    updateSchedule,
    deleteSchedule,
    fetchTodayDoses,
    markDose,
    fetchStats,
  }
}
