<script setup lang="ts">
import type { Receipt, ReceiptItem } from "~/types/api";
import { formatCurrency, formatDate } from "~/utils/formatters";

const props = defineProps<{
  receipt: Receipt;
}>();

const emit = defineEmits<{
  verified: [];
}>();

const { getReceiptImageUrl, verifyReceipt } = useReceipts();
const toast = useToast();
const isVerifying = ref(false);
const isImageViewerOpen = ref(false);

const imageUrl = computed(() => getReceiptImageUrl(props.receipt.image_path));

const openImageViewer = () => {
  isImageViewerOpen.value = true;
};

const handleVerify = async () => {
  if (!confirm("Mark this receipt as verified?")) return;

  isVerifying.value = true;
  try {
    await verifyReceipt(props.receipt.id);
    toast.add({
      title: "Success",
      description: "Receipt verified successfully",
      color: "green",
    });
    emit("verified");
  } catch (error) {
    toast.add({
      title: "Error",
      description:
        error instanceof Error ? error.message : "Failed to verify receipt",
      color: "red",
    });
  } finally {
    isVerifying.value = false;
  }
};

const items = ref<ReceiptItem[]>([]);
const updatingItems = ref(false);

// Parse items on mount and when receipt changes
const parseItems = () => {
  if (!props.receipt.items_json) {
    items.value = [];
    return;
  }
  try {
    items.value = JSON.parse(props.receipt.items_json);
  } catch (e) {
    console.error("Failed to parse items:", e);
    items.value = [];
  }
};

// Watch for receipt changes
watch(() => props.receipt.items_json, parseItems, { immediate: true });

const itemsTotal = computed(() => {
  return items.value.reduce((sum, item) => sum + item.total_price, 0);
});

// Handle item update
const handleItemUpdate = async (index: number, updatedItem: ReceiptItem) => {
  updatingItems.value = true;

  try {
    // Update local items array
    const newItems = [...items.value];
    newItems[index] = updatedItem;

    // Update receipt via API
    const { updateReceipt } = useReceipts();
    await updateReceipt(props.receipt.id, {
      items_json: JSON.stringify(newItems),
    });

    // Update local state
    items.value = newItems;

    toast.add({
      title: "Success",
      description: "Item updated successfully",
      color: "green",
    });
  } catch (error) {
    toast.add({
      title: "Error",
      description:
        error instanceof Error ? error.message : "Failed to update item",
      color: "red",
    });
  } finally {
    updatingItems.value = false;
  }
};
</script>

<template>
  <div class="space-y-6">
    <!-- Image Preview with View Button -->
    <div class="relative group">
      <div class="relative h-64 bg-card-black border border-border-gray rounded-lg overflow-hidden">
        <img
          :src="imageUrl"
          :alt="`Receipt from ${receipt.merchant || 'Unknown'}`"
          class="w-full h-full object-contain cursor-pointer transition-opacity group-hover:opacity-75"
          @click="openImageViewer"
        />
        <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            class="px-6 py-3 bg-cyber-blue text-pure-white rounded-lg font-semibold shadow-lg hover:bg-cyber-blue/90 transition-all transform hover:scale-105"
            @click="openImageViewer"
          >
            <UIcon name="i-heroicons-magnifying-glass-plus" class="w-5 h-5 inline mr-2" />
            View Full Size
          </button>
        </div>
      </div>
    </div>

    <!-- Basic Info -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <p class="text-sm font-medium text-pure-white/60">Merchant</p>
        <p class="mt-1 text-lg font-semibold text-pure-white">
          {{ receipt.merchant || "Unknown" }}
        </p>
      </div>
      <div>
        <p class="text-sm font-medium text-pure-white/60">Date</p>
        <p class="mt-1 text-lg font-semibold text-pure-white">
          {{ formatDate(receipt.scan_date) }}
        </p>
      </div>
      <div>
        <p class="text-sm font-medium text-pure-white/60">Total</p>
        <p class="mt-1 text-lg font-semibold text-electric-green">
          {{ receipt.total ? formatCurrency(receipt.total) : "N/A" }}
        </p>
      </div>
      <div>
        <p class="text-sm font-medium text-pure-white/60">Status</p>
        <div class="flex items-center gap-2 mt-1">
          <UBadge
            :color="receipt.verified ? 'success' : 'warning'"
            variant="solid"
            size="sm"
          >
            {{ receipt.verified ? "Verified" : "Pending" }}
          </UBadge>
          <BaseButton
            v-if="!receipt.verified"
            size="sm"
            variant="primary"
            icon="i-heroicons-check"
            :loading="isVerifying"
            @click="handleVerify"
          >
            Mark as Verified
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Items -->
    <div v-if="items.length > 0">
      <h3 class="text-lg font-semibold text-pure-white mb-3">Items</h3>
      <div class="border border-border-gray rounded-lg overflow-hidden">
        <table class="min-w-full divide-y divide-border-gray">
          <thead class="bg-card-black/50">
            <tr>
              <th
                class="px-4 py-3 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider"
              >
                Item
              </th>
              <th
                class="px-4 py-3 text-right text-xs font-medium text-pure-white/60 uppercase tracking-wider"
              >
                Qty
              </th>
              <th
                class="px-4 py-3 text-right text-xs font-medium text-pure-white/60 uppercase tracking-wider"
              >
                Unit Price
              </th>
              <th
                class="px-4 py-3 text-right text-xs font-medium text-pure-white/60 uppercase tracking-wider"
              >
                Total
              </th>
              <th
                class="px-4 py-3 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider"
              >
                Category
              </th>
              <th
                class="px-4 py-3 text-right text-xs font-medium text-pure-white/60 uppercase tracking-wider"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-card-black divide-y divide-border-gray">
            <ReceiptItemRow
              v-for="(item, index) in items"
              :key="index"
              :item="item"
              :index="index"
              :is-editable="!updatingItems"
              @update="(updatedItem) => handleItemUpdate(index, updatedItem)"
            />
            <tr class="bg-card-black/50 font-semibold">
              <td
                colspan="4"
                class="px-4 py-3 text-sm text-pure-white text-right"
              >
                Subtotal
              </td>
              <td
                colspan="2"
                class="px-4 py-3 text-sm text-electric-green text-right"
              >
                {{ formatCurrency(itemsTotal) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Raw OCR Response (Developer View) -->
    <details v-if="receipt.raw_ocr_response" class="text-sm">
      <summary
        class="cursor-pointer text-pure-white/60 hover:text-pure-white transition-colors"
      >
        Raw OCR Response
      </summary>
      <pre
        class="mt-2 p-3 bg-background-black border border-border-gray rounded text-xs overflow-x-auto text-pure-white/80"
        >{{ receipt.raw_ocr_response }}</pre
      >
    </details>

    <!-- Image Viewer Dialog -->
    <ImageViewerDialog
      v-model="isImageViewerOpen"
      :image-url="imageUrl"
      :title="`Receipt from ${receipt.merchant || 'Unknown'}`"
    />
  </div>
</template>
