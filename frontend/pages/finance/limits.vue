<script setup lang="ts">
import { formatCurrency } from '~/utils/formatters'
import type { BudgetSettings, CompleteBudgetStatus, Category } from '~/types/api'

// Page metadata
definePageMeta({
  layout: 'finance',
})

useSeoMeta({
  title: 'Budget Limits - LockIner',
  description: 'Manage your spending limits and monitor budget status',
})

const { currentHouseholdId, householdIdForApi, isPersonalContext } = useHouseholdContext()
const { getCompleteBudgetStatus, getBudgetSettings } = useAnalytics()
const { checkAndDisplayAlerts } = useBudgetAlerts()
const categoriesStore = useCategoriesStore()
const toast = useToast()

// Current month
const now = new Date()
const currentMonth = ref(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`)

// State
const budgetStatus = ref<CompleteBudgetStatus | null>(null)
const budgetSettings = ref<BudgetSettings | null>(null)
const loading = ref(false)
const showSettingsForm = ref(false)
const editingCategory = ref<Category | null>(null)
const showEditDialog = ref(false)

// Fetch data
const fetchData = async () => {
  loading.value = true
  try {
    const [status, settings] = await Promise.all([
      getCompleteBudgetStatus(currentMonth.value, householdIdForApi.value),
      getBudgetSettings(householdIdForApi.value),
      categoriesStore.fetchCategories(),
    ])

    budgetStatus.value = status
    budgetSettings.value = settings

    // Check for alerts
    await checkAndDisplayAlerts(currentMonth.value, false, householdIdForApi.value)
  } catch (error) {
    toast.add({
      title: 'Error',
      description: error instanceof Error ? error.message : 'Failed to load budget data',
      color: 'red',
    })
  } finally {
    loading.value = false
  }
}

// Handle settings update
const handleSettingsUpdated = (settings: BudgetSettings) => {
  budgetSettings.value = settings
  showSettingsForm.value = false
  fetchData() // Refresh data
}

// Handle budget update
const handleBudgetUpdated = () => {
  editingCategory.value = null
  showEditDialog.value = false
  fetchData() // Refresh data
}

// Open edit dialog
const openEditDialog = (category: Category) => {
  editingCategory.value = category
  showEditDialog.value = true
}

// Initial load
onMounted(() => {
  fetchData()
})

// Reload data when context changes
watch(() => currentHouseholdId.value, fetchData)

// Format month for display
const formatMonthDisplay = (month: string) => {
  const [year, monthNum] = month.split('-')
  const date = new Date(Number(year), Number(monthNum) - 1)
  return date.toLocaleDateString('pl-PL', { year: 'numeric', month: 'long' })
}
</script>

<template>
  <div class="max-w-7xl">
    <!-- Header -->
    <div class="mb-6 sm:mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-pure-white mb-2 flex items-center gap-2 sm:gap-3">
        <UIcon name="i-heroicons-scale" class="w-6 h-6 sm:w-8 sm:h-8 text-electric-green" />
        Budget Limits
      </h1>
      <p class="text-sm sm:text-base text-pure-white/60">Manage your spending limits and monitor budget status</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-electric-green mx-auto mb-4"
        ></div>
        <p class="text-pure-white/60">Loading budget data...</p>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="budgetStatus && budgetSettings" class="space-y-8">
      <!-- Overall Budget Card -->
      <OverallBudgetCard :budget="budgetStatus.overall" />

      <!-- Budget Settings Section -->
      <div class="bg-card-black border border-border-gray rounded-lg p-4 sm:p-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h2 class="text-xl sm:text-2xl font-semibold text-pure-white flex items-center gap-2">
              <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5 sm:w-6 sm:h-6" />
              Budget Settings
            </h2>
            <p class="text-xs sm:text-sm text-pure-white/60 mt-1">
              Configure your overall budget limit and alert preferences
            </p>
          </div>
          <BaseButton variant="secondary" size="sm" class="self-start sm:self-auto" @click="showSettingsForm = !showSettingsForm">
            {{ showSettingsForm ? 'Hide' : 'Edit Settings' }}
          </BaseButton>
        </div>

        <!-- Settings Form (Expandable) -->
        <Transition name="expand">
          <div v-if="showSettingsForm" class="mt-6 border-t border-border-gray pt-6">
            <BudgetSettingsForm :settings="budgetSettings" @settings-updated="handleSettingsUpdated" />
          </div>
        </Transition>

        <!-- Current Settings Summary (When Collapsed) -->
        <div v-if="!showSettingsForm" class="mt-4 grid grid-cols-3 gap-2 sm:gap-4">
          <div class="bg-background-black rounded-lg p-2 sm:p-4">
            <p class="text-[10px] sm:text-xs text-pure-white/60 mb-1">Overall Limit</p>
            <p class="text-sm sm:text-xl font-bold text-electric-green truncate">
              {{
                budgetSettings.overall_monthly_limit
                  ? formatCurrency(budgetSettings.overall_monthly_limit)
                  : 'Not Set'
              }}
            </p>
          </div>
          <div class="bg-background-black rounded-lg p-2 sm:p-4">
            <p class="text-[10px] sm:text-xs text-pure-white/60 mb-1">Warning At</p>
            <p class="text-sm sm:text-xl font-bold text-warning-orange">
              {{ budgetSettings.alert_threshold_warning }}%
            </p>
          </div>
          <div class="bg-background-black rounded-lg p-2 sm:p-4">
            <p class="text-[10px] sm:text-xs text-pure-white/60 mb-1">Alerts</p>
            <p
              class="text-sm sm:text-xl font-bold"
              :class="budgetSettings.enable_alerts ? 'text-electric-green' : 'text-pure-white/40'"
            >
              {{ budgetSettings.enable_alerts ? 'Enabled' : 'Disabled' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Category Budgets Section -->
      <div class="bg-card-black border border-border-gray rounded-lg p-4 sm:p-6">
        <div class="mb-4 sm:mb-6">
          <h2 class="text-xl sm:text-2xl font-semibold text-pure-white flex items-center gap-2">
            <UIcon name="i-heroicons-tag" class="w-5 h-5 sm:w-6 sm:h-6" />
            Category Budgets
          </h2>
          <p class="text-xs sm:text-sm text-pure-white/60 mt-1">
            Set individual budget limits for each spending category
          </p>
        </div>

        <!-- Categories List -->
        <div class="space-y-3">
          <div
            v-for="category in categoriesStore.categories"
            :key="category.id"
            class="bg-background-black rounded-lg p-3 sm:p-4 border border-border-gray hover:border-electric-green transition-colors"
          >
            <div class="flex items-center gap-2 sm:gap-3">
              <!-- Category Info -->
              <div class="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                <div
                  class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg flex items-center justify-center shrink-0"
                  :style="{ backgroundColor: (category.color || '#00d4ff') + '20' }"
                >
                  <CategoryIcon
                    :icon="category.icon"
                    :size="20"
                    class="sm:!w-6 sm:!h-6"
                    :color="category.color || '#00d4ff'"
                  />
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="text-sm sm:text-base font-semibold text-pure-white truncate">{{ category.name }}</h4>
                  <p class="text-xs sm:text-sm text-pure-white/60 truncate">
                    {{
                      category.budget_limit
                        ? `Limit: ${formatCurrency(category.budget_limit)}`
                        : 'No limit set'
                    }}
                  </p>
                </div>
              </div>

              <!-- Budget Status (if has limit and in current month status) -->
              <div v-if="category.budget_limit" class="hidden sm:flex items-center gap-4 mr-4">
                <div class="text-right">
                  <p class="text-xs text-pure-white/60">This Month</p>
                  <p class="text-sm font-semibold text-pure-white">
                    {{
                      formatCurrency(
                        budgetStatus.categories.find((c) => c.category === category.name)?.spent || 0
                      )
                    }}
                  </p>
                </div>
                <div
                  class="w-12 h-12 rounded-full border-4 flex items-center justify-center"
                  :class="
                    budgetStatus.categories.find((c) => c.category === category.name)?.status === 'over'
                      ? 'border-danger-red text-danger-red'
                      : budgetStatus.categories.find((c) => c.category === category.name)?.status ===
                        'warning'
                      ? 'border-warning-orange text-warning-orange'
                      : 'border-electric-green text-electric-green'
                  "
                >
                  <span class="text-xs font-bold">
                    {{
                      (
                        budgetStatus.categories.find((c) => c.category === category.name)?.percentage || 0
                      ).toFixed(0)
                    }}%
                  </span>
                </div>
              </div>

              <!-- Mobile: Small percentage badge -->
              <div
                v-if="category.budget_limit"
                class="flex sm:hidden items-center justify-center w-10 h-10 rounded-full border-2 shrink-0"
                :class="
                  budgetStatus.categories.find((c) => c.category === category.name)?.status === 'over'
                    ? 'border-danger-red text-danger-red'
                    : budgetStatus.categories.find((c) => c.category === category.name)?.status ===
                      'warning'
                    ? 'border-warning-orange text-warning-orange'
                    : 'border-electric-green text-electric-green'
                "
              >
                <span class="text-[10px] font-bold">
                  {{
                    (
                      budgetStatus.categories.find((c) => c.category === category.name)?.percentage || 0
                    ).toFixed(0)
                  }}%
                </span>
              </div>

              <!-- Edit Button -->
              <BaseButton variant="secondary" size="sm" class="shrink-0" @click="openEditDialog(category)">
                <UIcon name="i-heroicons-pencil" class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              </BaseButton>
            </div>
          </div>

          <!-- Empty State -->
          <p
            v-if="categoriesStore.categories.length === 0"
            class="text-center text-pure-white/40 py-8"
          >
            No categories found. Create categories first to set budget limits.
          </p>
        </div>
      </div>

      <!-- Budget Status for Current Month -->
      <div class="bg-card-black border border-border-gray rounded-lg p-4 sm:p-6">
        <div class="mb-4">
          <h2 class="text-lg sm:text-2xl font-semibold text-pure-white flex items-center gap-2">
            <UIcon name="i-heroicons-chart-bar" class="w-5 h-5 sm:w-6 sm:h-6" />
            <span class="truncate">Budget Status - {{ formatMonthDisplay(currentMonth) }}</span>
          </h2>
        </div>

        <BudgetProgress v-if="budgetStatus.categories.length > 0" :budgets="budgetStatus.categories" />
        <p v-else class="text-center text-pure-white/40 py-8">No category budgets configured yet.</p>
      </div>
    </div>

    <!-- Edit Category Budget Dialog -->
    <EditCategoryBudgetDialog
      v-if="editingCategory"
      v-model="showEditDialog"
      :category="editingCategory"
      @budget-updated="handleBudgetUpdated"
    />
  </div>
</template>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 1000px;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
