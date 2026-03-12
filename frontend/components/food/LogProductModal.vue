<script setup lang="ts">
import type { ProductSearchResult, InventoryItemForProduct, DirectConsumptionRequest } from '~/composables/useFoodNutrition'

const props = defineProps<{
  result: ProductSearchResult
  open: boolean
}>()

const emit = defineEmits<{
  close: []
  logged: []
}>()

const { t } = useI18n()
const { consumeInventoryItem, logDirect } = useFoodNutrition()
const toast = useToast()

const quantity = ref(100)
const unit = ref('g')
const mealType = ref('snack')
const notes = ref('')
const selectedInventoryId = ref<number | null>(null)
const useInventory = ref(false)
const loading = ref(false)

const mealTypes = computed(() => [
  { key: 'breakfast', label: t('food.breakfast'), icon: '🌅' },
  { key: 'lunch', label: t('food.lunch'), icon: '☀️' },
  { key: 'dinner', label: t('food.dinner'), icon: '🌙' },
  { key: 'snack', label: t('food.snack'), icon: '🍎' },
])

const productName = computed(() => {
  if (props.result.product) return props.result.product.name
  if (props.result.off_product) return props.result.off_product.name || 'Product'
  return 'Product'
})

const kcalPer100 = computed(() => {
  if (props.result.product) return props.result.product.calories
  if (props.result.off_product) return props.result.off_product.calories_100g
  return null
})

const estimatedKcal = computed(() => {
  if (!kcalPer100.value) return null
  let factor = 1
  if (unit.value === 'g' || unit.value === 'ml') factor = quantity.value / 100
  else if (unit.value === 'kg' || unit.value === 'l') factor = quantity.value * 10
  else factor = quantity.value
  return Math.round(kcalPer100.value * factor)
})

const hasInventory = computed(() => props.result.inventory_items.length > 0)

watch(() => props.open, (val) => {
  if (val) {
    const defaultUnit = props.result.product?.default_unit || 'g'
    unit.value = defaultUnit
    quantity.value = ['g', 'ml'].includes(defaultUnit) ? 100 : 1
    useInventory.value = hasInventory.value
    selectedInventoryId.value = hasInventory.value ? props.result.inventory_items[0].id : null
    if (hasInventory.value) {
      const first = props.result.inventory_items[0]
      quantity.value = first.quantity
      unit.value = first.unit
    }
  }
})

function selectInventoryItem(item: InventoryItemForProduct) {
  selectedInventoryId.value = item.id
  useInventory.value = true
  quantity.value = item.quantity
  unit.value = item.unit
}

async function submit() {
  loading.value = true
  try {
    if (useInventory.value && selectedInventoryId.value) {
      await consumeInventoryItem(selectedInventoryId.value, {
        quantity: quantity.value,
        meal_type: mealType.value,
        notes: notes.value || undefined,
      })
    } else {
      const req: DirectConsumptionRequest = {
        quantity: quantity.value,
        unit: unit.value,
        meal_type: mealType.value,
        notes: notes.value || undefined,
      }
      if (props.result.product) req.product_id = props.result.product.id
      else if (props.result.off_product) {
        req.off_product_code = props.result.off_product.code
        req.product_name = props.result.off_product.name
      }
      await logDirect(req)
    }
    toast.add({ title: t('food.logged_success'), color: 'green' })
    emit('logged')
    emit('close')
  } catch (e: any) {
    toast.add({ title: t('food.log_error'), description: e?.data?.detail || '', color: 'red' })
  } finally {
    loading.value = false
  }
}

function locationLabel(loc: string) {
  const map: Record<string, string> = {
    fridge: '🧊 ' + t('food.fridge'),
    freezer: '❄️ ' + t('food.freezer'),
    pantry: '🗄️ ' + t('food.pantry'),
  }
  return map[loc] || loc
}
</script>

<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
      >
        <!-- Overlay -->
        <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="emit('close')" />

        <!-- Panel -->
        <div class="relative w-full sm:max-w-md bg-card-black border border-border-gray rounded-t-2xl sm:rounded-2xl p-5 space-y-4 max-h-[90vh] overflow-y-auto">
          <!-- Header -->
          <div class="flex items-start justify-between">
            <div>
              <h3 class="text-pure-white font-semibold text-lg leading-tight">{{ productName }}</h3>
              <div class="flex flex-wrap gap-2 mt-1">
                <span v-if="kcalPer100" class="text-gray-400 text-sm">{{ kcalPer100 }} {{ $t('food.kcal_per_100g') }}</span>
                <span v-if="result.source === 'off'" class="text-xs bg-warning-orange/20 text-warning-orange px-1.5 py-0.5 rounded font-medium">
                  {{ $t('food.product_off') }}
                </span>
                <span v-if="result.source === 'local'" class="text-xs bg-electric-green/20 text-electric-green px-1.5 py-0.5 rounded font-medium">
                  {{ $t('food.product_local') }}
                </span>
              </div>
            </div>
            <button class="p-1 text-gray-400 hover:text-pure-white transition-colors" @click="emit('close')">
              <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
            </button>
          </div>

          <!-- Inventory items (FIFO) -->
          <div v-if="hasInventory" class="space-y-1.5">
            <p class="text-xs text-gray-400 uppercase tracking-wide font-medium">{{ $t('food.use_from_pantry') }}</p>
            <div
              v-for="item in result.inventory_items"
              :key="item.id"
              class="flex items-center gap-2.5 p-2.5 rounded-xl cursor-pointer border transition-colors"
              :class="selectedInventoryId === item.id && useInventory
                ? 'border-electric-green bg-electric-green/10'
                : 'border-border-gray hover:border-gray-500'"
              @click="selectInventoryItem(item)"
            >
              <div class="w-4 h-4 rounded-full border-2 flex-shrink-0 flex items-center justify-center"
                   :class="selectedInventoryId === item.id && useInventory ? 'border-electric-green' : 'border-gray-500'">
                <div v-if="selectedInventoryId === item.id && useInventory" class="w-2 h-2 rounded-full bg-electric-green" />
              </div>
              <span class="text-sm text-pure-white flex-1">{{ locationLabel(item.location) }} — {{ item.quantity }} {{ item.unit }}</span>
              <span v-if="item.expiry_date" class="text-xs text-gray-400 flex items-center gap-1 flex-shrink-0">
                <UIcon name="i-heroicons-calendar-days" class="w-3 h-3" />
                {{ item.expiry_date }}
              </span>
            </div>
            <!-- Direct log option -->
            <div
              class="flex items-center gap-2.5 p-2.5 rounded-xl cursor-pointer border transition-colors"
              :class="!useInventory ? 'border-cyber-blue bg-cyber-blue/10' : 'border-border-gray hover:border-gray-500'"
              @click="useInventory = false; selectedInventoryId = null"
            >
              <div class="w-4 h-4 rounded-full border-2 flex-shrink-0 flex items-center justify-center"
                   :class="!useInventory ? 'border-cyber-blue' : 'border-gray-500'">
                <div v-if="!useInventory" class="w-2 h-2 rounded-full bg-cyber-blue" />
              </div>
              <span class="text-sm text-gray-300">{{ $t('food.no_inventory_use') }}</span>
            </div>
          </div>

          <!-- Quantity + unit -->
          <div class="flex gap-2">
            <div class="flex-1">
              <label class="text-xs text-gray-400 mb-1.5 block">{{ $t('food.quantity') }}</label>
              <input
                v-model.number="quantity"
                type="number"
                min="0.1"
                step="0.1"
                class="w-full px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white text-sm focus:outline-none focus:border-electric-green transition-colors"
              />
            </div>
            <div class="w-24">
              <label class="text-xs text-gray-400 mb-1.5 block">{{ $t('food.unit') }}</label>
              <select
                v-model="unit"
                class="w-full px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white text-sm focus:outline-none focus:border-electric-green transition-colors"
              >
                <option v-for="u in ['g', 'ml', 'kg', 'l', 'szt']" :key="u" :value="u">{{ u }}</option>
              </select>
            </div>
          </div>

          <!-- Estimated kcal -->
          <div v-if="estimatedKcal !== null" class="text-center py-1">
            <span class="text-electric-green font-bold text-2xl">{{ estimatedKcal }}</span>
            <span class="text-gray-400 text-sm ml-1">{{ $t('food.est_kcal') }}</span>
          </div>

          <!-- Meal type -->
          <div>
            <label class="text-xs text-gray-400 uppercase tracking-wide font-medium block mb-2">{{ $t('food.meal_type') }}</label>
            <div class="grid grid-cols-4 gap-1.5">
              <button
                v-for="m in mealTypes"
                :key="m.key"
                class="flex flex-col items-center p-2 rounded-xl border text-xs transition-colors"
                :class="mealType === m.key
                  ? 'border-electric-green bg-electric-green/15 text-pure-white'
                  : 'border-border-gray text-gray-400 hover:border-gray-500'"
                @click="mealType = m.key"
              >
                <span class="text-base mb-0.5">{{ m.icon }}</span>
                <span class="leading-tight text-center">{{ m.label }}</span>
              </button>
            </div>
          </div>

          <!-- Submit -->
          <BaseButton
            variant="primary"
            size="md"
            :loading="loading"
            :disabled="quantity <= 0"
            class="w-full"
            @click="submit"
          >
            {{ useInventory && selectedInventoryId ? $t('food.use_from_pantry_btn') : $t('food.log_btn') }}
          </BaseButton>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.25s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
