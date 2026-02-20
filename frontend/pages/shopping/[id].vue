<script setup lang="ts">
import type { ShoppingListItem, ShoppingListItemCreate, ShoppingItemStatus } from '~/types/shopping'

definePageMeta({ layout: 'shopping' })

const route = useRoute()
const listId = computed(() => Number(route.params.id))

const {
  currentList,
  loading,
  pendingItems,
  inCartItems,
  purchasedItems,
  itemsByCategory,
  progressPercent,
  fetchList,
  completeList,
  updateList,
  addItem,
  updateItemStatus,
  deleteItem,
} = useShoppingLists()

onMounted(() => fetchList(listId.value))

// ----------------------------------------------------------
// Quick add
// ----------------------------------------------------------
const showQuickAdd = ref(false)

async function onItemAdded(data: ShoppingListItemCreate) {
  await addItem(listId.value, data)
}

// ----------------------------------------------------------
// Edit item inline
// ----------------------------------------------------------
const editingItem = ref<ShoppingListItem | null>(null)
const editForm = reactive({ name: '', quantity: null as number | null, unit: null as string | null, category: null as string | null, notes: null as string | null })

function startEdit(item: ShoppingListItem) {
  editingItem.value = item
  editForm.name = item.name
  editForm.quantity = item.quantity
  editForm.unit = item.unit
  editForm.category = item.category
  editForm.notes = item.notes
}

// ----------------------------------------------------------
// Complete list
// ----------------------------------------------------------
const completing = ref(false)

async function handleComplete() {
  completing.value = true
  try {
    await completeList(listId.value)
    navigateTo('/shopping')
  } finally {
    completing.value = false
  }
}

// ----------------------------------------------------------
// Edit list name / store inline
// ----------------------------------------------------------
const editingListMeta = ref(false)
const listMetaForm = reactive({ name: '', store_name: null as string | null })

function startEditListMeta() {
  if (!currentList.value) return
  listMetaForm.name = currentList.value.name
  listMetaForm.store_name = currentList.value.store_name
  editingListMeta.value = true
}

async function saveListMeta() {
  await updateList(listId.value, { name: listMetaForm.name, store_name: listMetaForm.store_name || null })
  editingListMeta.value = false
}

const progressColor = computed(() => {
  if (progressPercent.value === 100) return 'bg-electric-green'
  if (progressPercent.value >= 50) return 'bg-warning-orange'
  return 'bg-warning-orange'
})
</script>

<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <span class="i-heroicons-arrow-path animate-spin text-2xl text-border-gray" />
    </div>

    <template v-else-if="currentList">
      <!-- Header -->
      <div class="space-y-1">
        <div class="flex items-start justify-between gap-4">
          <div v-if="!editingListMeta" class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <h1 class="text-xl font-bold text-pure-white">{{ currentList.name }}</h1>
              <span
                v-if="currentList.visibility === 'household'"
                class="text-xs px-2 py-0.5 bg-warning-orange/10 text-warning-orange rounded-full border border-warning-orange/20"
              >
                Household
              </span>
              <span
                v-if="currentList.status === 'completed'"
                class="text-xs px-2 py-0.5 bg-electric-green/10 text-electric-green rounded-full"
              >
                Completed
              </span>
            </div>
            <p v-if="currentList.store_name" class="text-sm text-border-gray mt-0.5 flex items-center gap-1">
              <span class="i-heroicons-map-pin text-xs" />
              {{ currentList.store_name }}
            </p>
          </div>

          <!-- Inline meta edit -->
          <div v-else class="flex-1 space-y-2">
            <input
              v-model="listMetaForm.name"
              type="text"
              class="w-full bg-background-black border border-warning-orange rounded-lg px-3 py-1.5 text-sm text-pure-white focus:outline-none"
              @keydown.enter="saveListMeta"
              @keydown.escape="editingListMeta = false"
            />
            <input
              v-model="listMetaForm.store_name"
              type="text"
              placeholder="Store name (optional)"
              class="w-full bg-background-black border border-border-gray rounded-lg px-3 py-1.5 text-sm text-pure-white placeholder-border-gray focus:border-warning-orange focus:outline-none"
            />
            <div class="flex gap-2">
              <BaseButton variant="primary" size="sm" @click="saveListMeta">Save</BaseButton>
              <BaseButton variant="ghost" size="sm" @click="editingListMeta = false">Cancel</BaseButton>
            </div>
          </div>

          <div v-if="!editingListMeta" class="flex items-center gap-2 flex-shrink-0">
            <button
              class="p-1.5 rounded-lg text-border-gray hover:text-pure-white hover:bg-card-black transition-colors"
              title="Edit list"
              @click="startEditListMeta"
            >
              <span class="i-heroicons-pencil text-sm" />
            </button>
            <NuxtLink
              to="/shopping"
              class="p-1.5 rounded-lg text-border-gray hover:text-pure-white hover:bg-card-black transition-colors"
              title="Back to lists"
            >
              <span class="i-heroicons-arrow-left text-sm" />
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Progress bar -->
      <div v-if="currentList.items.length > 0" class="space-y-2">
        <div class="flex items-center justify-between text-xs text-border-gray">
          <span>{{ purchasedItems.length }}/{{ currentList.items.length }} purchased</span>
          <span v-if="inCartItems.length > 0" class="text-warning-orange">
            {{ inCartItems.length }} in cart
          </span>
          <span v-if="progressPercent === 100" class="text-electric-green font-medium">All done!</span>
        </div>
        <div class="h-1.5 bg-background-black rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="progressColor"
            :style="{ width: `${progressPercent}%` }"
          />
        </div>
      </div>

      <!-- Status legend -->
      <div class="flex items-center gap-4 text-xs text-border-gray">
        <span class="flex items-center gap-1">
          <span class="i-heroicons-circle text-border-gray" /> Pending
        </span>
        <span class="flex items-center gap-1">
          <span class="i-heroicons-shopping-cart text-warning-orange" /> In cart
        </span>
        <span class="flex items-center gap-1">
          <span class="i-heroicons-check-circle text-electric-green" /> Purchased
        </span>
        <span class="text-border-gray/50">(tap icon to cycle)</span>
      </div>

      <!-- Items by category -->
      <div v-if="currentList.items.length > 0" class="space-y-4">
        <!-- Active items grouped by category -->
        <template v-for="(items, category) in itemsByCategory" :key="category">
          <div class="space-y-2">
            <h3 class="text-xs font-semibold text-border-gray uppercase tracking-wider px-1">
              {{ category }}
            </h3>
            <ShoppingItemRow
              v-for="item in items"
              :key="item.id"
              :item="item"
              @status-change="updateItemStatus"
              @edit="startEdit"
              @delete="deleteItem"
            />
          </div>
        </template>

        <!-- Purchased items (collapsed) -->
        <details v-if="purchasedItems.length > 0" class="mt-2">
          <summary class="text-xs text-border-gray cursor-pointer hover:text-pure-white transition-colors select-none">
            Purchased ({{ purchasedItems.length }})
          </summary>
          <div class="mt-2 space-y-2">
            <ShoppingItemRow
              v-for="item in purchasedItems"
              :key="item.id"
              :item="item"
              @status-change="updateItemStatus"
              @edit="startEdit"
              @delete="deleteItem"
            />
          </div>
        </details>
      </div>

      <!-- Empty state -->
      <p v-else class="text-center text-sm text-border-gray py-8">
        The list is empty. Add your first item!
      </p>

      <!-- Quick add -->
      <div>
        <ShoppingQuickAdd
          v-if="showQuickAdd"
          :list-id="listId"
          @added="onItemAdded"
          @cancel="showQuickAdd = false"
        />
        <div v-else class="flex flex-col items-center gap-3">
          <BaseButton
            variant="primary"
            class="max-w-xs w-full"
            @click="showQuickAdd = true"
          >
            <span class="i-heroicons-plus text-sm mr-1" />
            Add item
          </BaseButton>

          <!-- Complete list button -->
          <BaseButton
            v-if="currentList.status === 'active' && currentList.items.length > 0"
            variant="secondary"
            class="max-w-xs w-full"
            :loading="completing"
            @click="handleComplete"
          >
            <span class="i-heroicons-check text-sm mr-1" />
            Mark as completed
          </BaseButton>
        </div>
      </div>
    </template>

    <!-- 404 -->
    <div v-else class="text-center py-16">
      <p class="text-pure-white font-medium">List not found</p>
      <NuxtLink to="/shopping" class="text-sm text-warning-orange hover:underline mt-2 block">
        Back to lists
      </NuxtLink>
    </div>
  </div>
</template>
