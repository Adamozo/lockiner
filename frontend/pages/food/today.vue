<script setup lang="ts">
import type { ProductSearchResult, DailyNutritionSummary } from '~/composables/useFoodNutrition'

definePageMeta({ layout: 'food' })

const { t } = useI18n()
const { searchGlobal, fetchDailySummary, deleteLog } = useFoodNutrition()
const toast = useToast()

// Mobile tab state
const mobileTab = ref<'log' | 'today'>('today')

// --- Log side ---
const searchQuery = ref('')
const searchResults = ref<ProductSearchResult[]>([])
const searching = ref(false)
const showScanner = ref(false)
const selectedResult = ref<ProductSearchResult | null>(null)
const showLogModal = ref(false)

let searchTimer: ReturnType<typeof setTimeout> | null = null

async function doSearch() {
  const q = searchQuery.value.trim()
  if (!q) return
  searching.value = true
  try {
    searchResults.value = await searchGlobal(q)
  } catch {
    searchResults.value = []
  } finally {
    searching.value = false
  }
}

function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  const q = searchQuery.value.trim()
  if (q.length < 3) return
  searchTimer = setTimeout(doSearch, 400)
}

function clearSearch() {
  searchQuery.value = ''
  searchResults.value = []
  if (searchTimer) clearTimeout(searchTimer)
}

async function handleScanned(ean: string) {
  showScanner.value = false
  const { scanBarcode } = useFoodNutrition()
  const result = await scanBarcode(ean)
  if (result) {
    selectedResult.value = result
    showLogModal.value = true
  } else {
    toast.add({ title: t('food.scan_not_found'), description: `EAN: ${ean}`, color: 'orange' })
  }
}

function selectProduct(result: ProductSearchResult) {
  selectedResult.value = result
  showLogModal.value = true
}

function productDisplayName(r: ProductSearchResult) {
  return r.product?.name || r.off_product?.name || 'Product'
}

function productKcal(r: ProductSearchResult) {
  return r.product?.calories ?? r.off_product?.calories_100g ?? null
}

// --- Today side ---
const currentDate = ref(new Date().toISOString().slice(0, 10))
const summary = ref<DailyNutritionSummary | null>(null)
const loadingSummary = ref(false)

async function loadSummary() {
  loadingSummary.value = true
  try {
    summary.value = await fetchDailySummary(currentDate.value)
  } catch {
    summary.value = null
  } finally {
    loadingSummary.value = false
  }
}

function prevDay() {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() - 1)
  currentDate.value = d.toISOString().slice(0, 10)
}

function nextDay() {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + 1)
  currentDate.value = d.toISOString().slice(0, 10)
}

const isToday = computed(() => currentDate.value === new Date().toISOString().slice(0, 10))

const displayDate = computed(() => {
  if (isToday.value) return t('food.today')
  const d = new Date(currentDate.value + 'T12:00:00')
  const locale = useI18n().locale.value === 'pl' ? 'pl-PL' : 'en-US'
  return d.toLocaleDateString(locale, { weekday: 'short', day: 'numeric', month: 'short' })
})

async function removeLog(logId: number) {
  try {
    await deleteLog(logId)
    toast.add({ title: t('common.success'), color: 'green' })
    await loadSummary()
  } catch {
    toast.add({ title: t('food.delete_log_error'), color: 'red' })
  }
}

function onLogged() {
  showLogModal.value = false
  selectedResult.value = null
  loadSummary()
}

const mealLabels = computed<Record<string, string>>(() => ({
  breakfast: t('food.breakfast'),
  lunch: t('food.lunch'),
  dinner: t('food.dinner'),
  snack: t('food.snack'),
  other: t('food.other'),
}))

const mealIcons: Record<string, string> = {
  breakfast: '🌅',
  lunch: '☀️',
  dinner: '🌙',
  snack: '🍎',
  other: '🍽️',
}

watch(currentDate, loadSummary)
onMounted(loadSummary)
</script>

<template>
  <div>
    <!-- Mobile tab switcher -->
    <div class="lg:hidden flex border border-border-gray rounded-xl overflow-hidden mb-4">
      <button
        class="flex-1 py-2.5 text-sm font-medium transition-colors"
        :class="mobileTab === 'log'
          ? 'bg-electric-green/15 text-electric-green'
          : 'bg-card-black text-pure-white/60 hover:text-pure-white'"
        @click="mobileTab = 'log'"
      >
        <UIcon name="i-heroicons-plus-circle" class="w-4 h-4 inline mr-1.5" />
        {{ $t('food.log_tab') }}
      </button>
      <button
        class="flex-1 py-2.5 text-sm font-medium transition-colors border-l border-border-gray"
        :class="mobileTab === 'today'
          ? 'bg-electric-green/15 text-electric-green'
          : 'bg-card-black text-pure-white/60 hover:text-pure-white'"
        @click="mobileTab = 'today'"
      >
        <UIcon name="i-heroicons-sun" class="w-4 h-4 inline mr-1.5" />
        {{ $t('food.today_tab') }}
      </button>
    </div>

    <!-- Desktop: 2 columns | Mobile: single panel based on tab -->
    <div class="lg:grid lg:grid-cols-2 lg:gap-6">

      <!-- LEFT: Log food -->
      <div :class="{ 'hidden lg:block': mobileTab === 'today' }" class="space-y-4">
        <h2 class="text-pure-white font-bold text-xl hidden lg:block">{{ $t('food.log_meal') }}</h2>

        <!-- Search bar -->
        <div class="flex gap-2">
          <div class="relative flex-1">
            <UIcon name="i-heroicons-magnifying-glass" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="$t('food.search_placeholder')"
              class="w-full pl-9 pr-8 py-2.5 bg-card-black border border-border-gray rounded-lg text-pure-white placeholder-gray-500 focus:outline-none focus:border-electric-green transition-colors text-sm"
              @input="onSearchInput"
              @keyup.enter="doSearch"
            />
            <button
              v-if="searchQuery"
              class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-500 hover:text-pure-white transition-colors"
              @click="clearSearch"
            >
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            </button>
          </div>
          <button
            class="p-2.5 bg-card-black border border-border-gray rounded-lg text-gray-400 hover:text-electric-green hover:border-electric-green transition-colors"
            :title="$t('food.scan_ean')"
            @click="showScanner = true"
          >
            <UIcon name="i-heroicons-camera" class="w-5 h-5" />
          </button>
          <BaseButton variant="primary" size="sm" :loading="searching" @click="doSearch">
            {{ $t('food.search') }}
          </BaseButton>
        </div>

        <!-- Search results -->
        <div v-if="searching" class="flex justify-center py-8">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 text-electric-green animate-spin" />
        </div>

        <div v-else-if="searchResults.length > 0" class="space-y-2">
          <div
            v-for="(result, idx) in searchResults"
            :key="idx"
            class="bg-card-black border border-border-gray rounded-xl px-3 py-2.5 flex items-center gap-3 cursor-pointer hover:border-electric-green transition-colors group"
            @click="selectProduct(result)"
          >
            <div class="flex-1 min-w-0">
              <!-- Row 1: name + badges -->
              <div class="flex flex-wrap items-center gap-1.5">
                <span class="text-pure-white font-medium text-sm truncate">{{ productDisplayName(result) }}</span>
                <span v-if="result.in_stock" class="text-xs bg-electric-green/20 text-electric-green px-1.5 py-0.5 rounded-md font-medium flex-shrink-0">
                  {{ $t('food.in_stock') }}
                </span>
                <span v-if="result.source === 'off'" class="text-xs bg-gray-700 text-gray-300 px-1.5 py-0.5 rounded-md flex-shrink-0">
                  {{ $t('food.product_off') }}
                </span>
                <span
                  v-if="['a','b','c','d','e'].includes(result.off_product?.nutriscore_grade ?? '')"
                  class="text-xs font-bold px-1.5 py-0.5 rounded-md uppercase flex-shrink-0"
                  :class="{
                    'bg-green-600/30 text-green-400': result.off_product!.nutriscore_grade === 'a',
                    'bg-lime-600/30 text-lime-400': result.off_product!.nutriscore_grade === 'b',
                    'bg-yellow-600/30 text-yellow-400': result.off_product!.nutriscore_grade === 'c',
                    'bg-orange-600/30 text-orange-400': result.off_product!.nutriscore_grade === 'd',
                    'bg-red-600/30 text-red-400': result.off_product!.nutriscore_grade === 'e',
                  }"
                >
                  {{ result.off_product!.nutriscore_grade!.toUpperCase() }}
                </span>
              </div>
              <!-- Row 2: brand · quantity · kcal -->
              <div class="flex items-center gap-1.5 mt-0.5 text-xs text-gray-400 flex-wrap">
                <span v-if="result.off_product?.brands" class="truncate max-w-[120px]">{{ result.off_product.brands.split(',')[0].trim() }}</span>
                <span v-if="result.off_product?.brands && (result.off_product?.quantity || productKcal(result))" class="text-gray-600">·</span>
                <span v-if="result.off_product?.quantity">{{ result.off_product.quantity }}</span>
                <span v-if="result.off_product?.quantity && productKcal(result)" class="text-gray-600">·</span>
                <span v-if="productKcal(result)">{{ productKcal(result) }} {{ $t('food.kcal_per_100g') }}</span>
              </div>
            </div>
            <UIcon name="i-heroicons-plus-circle" class="w-5 h-5 text-gray-500 group-hover:text-electric-green transition-colors flex-shrink-0" />
          </div>
        </div>

        <div v-else-if="searchQuery.trim() && !searching" class="bg-card-black border border-border-gray rounded-xl p-8 text-center">
          <UIcon name="i-heroicons-magnifying-glass" class="w-10 h-10 text-gray-600 mx-auto mb-2" />
          <p class="text-gray-400 text-sm">{{ $t('food.scan_not_found') }}</p>
          <p class="text-gray-600 text-xs mt-1">"{{ searchQuery }}"</p>
        </div>

        <div v-else class="bg-card-black border border-dashed border-border-gray rounded-xl p-8 text-center">
          <UIcon name="i-heroicons-magnifying-glass" class="w-10 h-10 text-gray-600 mx-auto mb-2" />
          <p class="text-gray-500 text-sm">{{ $t('food.search_placeholder') }}</p>
        </div>
      </div>

      <!-- RIGHT: Daily summary -->
      <div :class="{ 'hidden lg:block': mobileTab === 'log' }" class="space-y-4">
        <!-- Date navigation -->
        <div class="flex items-center justify-between">
          <button
            class="p-1.5 rounded-lg text-gray-400 hover:text-pure-white hover:bg-card-black transition-colors"
            @click="prevDay"
          >
            <UIcon name="i-heroicons-chevron-left" class="w-5 h-5" />
          </button>
          <h2 class="text-pure-white font-bold text-xl">{{ displayDate }}</h2>
          <button
            class="p-1.5 rounded-lg text-gray-400 hover:text-pure-white hover:bg-card-black transition-colors disabled:opacity-30"
            :disabled="isToday"
            @click="nextDay"
          >
            <UIcon name="i-heroicons-chevron-right" class="w-5 h-5" />
          </button>
        </div>

        <!-- Loading -->
        <div v-if="loadingSummary" class="flex justify-center py-10">
          <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 text-electric-green animate-spin" />
        </div>

        <template v-else-if="summary">
          <!-- Calorie ring -->
          <div class="bg-card-black border border-border-gray rounded-xl p-5 flex justify-center">
            <FoodDayCalorieRing
              :consumed="summary.total.calories"
              :goal="summary.goal?.calories || 2000"
              :protein="summary.total.protein"
              :carbohydrates="summary.total.carbohydrates"
              :fat="summary.total.fat"
              :protein-goal="summary.goal?.protein || undefined"
              :carb-goal="summary.goal?.carbohydrates || undefined"
              :fat-goal="summary.goal?.fat || undefined"
            />
          </div>

          <!-- Meals -->
          <div v-if="summary.by_meal.length > 0" class="space-y-2">
            <div
              v-for="meal in summary.by_meal"
              :key="meal.meal_type"
              class="bg-card-black border border-border-gray rounded-xl overflow-hidden"
            >
              <div class="flex items-center justify-between px-4 py-2.5 border-b border-border-gray">
                <span class="text-pure-white font-medium text-sm">
                  {{ mealIcons[meal.meal_type] || '🍽️' }}
                  {{ mealLabels[meal.meal_type] || meal.meal_type }}
                </span>
                <span class="text-electric-green font-semibold text-sm">{{ Math.round(meal.total_calories) }} kcal</span>
              </div>
              <div class="divide-y divide-border-gray">
                <div
                  v-for="entry in meal.logs"
                  :key="entry.id"
                  class="flex items-center justify-between px-4 py-2 group"
                >
                  <div class="flex-1 min-w-0 mr-3">
                    <span class="text-pure-white text-sm truncate block">{{ entry.product_name }}</span>
                    <span class="text-gray-500 text-xs">{{ entry.quantity }} {{ entry.unit }}</span>
                  </div>
                  <div class="flex items-center gap-2 flex-shrink-0">
                    <span v-if="entry.calories" class="text-gray-300 text-sm tabular-nums">{{ Math.round(entry.calories) }} kcal</span>
                    <button
                      class="opacity-0 group-hover:opacity-100 p-1 rounded text-gray-500 hover:text-danger-red hover:bg-danger-red/10 transition-all"
                      @click="removeLog(entry.id)"
                    >
                      <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="bg-card-black border border-border-gray rounded-xl p-8 text-center">
            <UIcon name="i-heroicons-clipboard-document-list" class="w-10 h-10 text-gray-600 mx-auto mb-2" />
            <p class="text-gray-400 text-sm">{{ $t('food.no_logs') }}</p>
          </div>

          <!-- Link to trend -->
          <div class="flex justify-end">
            <NuxtLink to="/fitness/nutrition">
              <BaseButton variant="secondary" size="sm">
                {{ $t('food.go_to_trend') }}
              </BaseButton>
            </NuxtLink>
          </div>
        </template>
      </div>
    </div>

    <!-- Barcode scanner overlay -->
    <FoodBarcodeScanner
      v-if="showScanner"
      @scanned="handleScanned"
      @close="showScanner = false"
    />

    <!-- Log product modal -->
    <FoodLogProductModal
      v-if="selectedResult"
      :result="selectedResult"
      :open="showLogModal"
      @close="showLogModal = false; selectedResult = null"
      @logged="onLogged"
    />
  </div>
</template>
