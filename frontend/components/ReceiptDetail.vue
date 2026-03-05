<script setup lang="ts">
import type { Receipt, ReceiptItem } from "~/types/api";
import { formatCurrency, formatDate } from "~/utils/formatters";

const props = defineProps<{
  receipt: Receipt;
}>();

const emit = defineEmits<{
  verified: [];
}>();

const { getReceiptImageUrl, verifyReceipt, addReceiptImage } = useReceipts();
const toast = useToast();
const isVerifying = ref(false);
const isImageViewerOpen = ref(false);
const isAddingPhoto = ref(false);
const addPhotoInputRef = ref<HTMLInputElement | null>(null);
const currentImageIndex = ref(0);

const allImages = computed(() => {
  const extra = props.receipt.additional_images ?? [];
  return [props.receipt.image_path, ...extra];
});

const currentImageUrl = computed(() =>
  getReceiptImageUrl(allImages.value[currentImageIndex.value])
);

const imageUrl = computed(() => getReceiptImageUrl(props.receipt.image_path));

const openImageViewer = () => {
  isImageViewerOpen.value = true;
};

const prevImage = () => {
  if (currentImageIndex.value > 0) currentImageIndex.value--;
};

const nextImage = () => {
  if (currentImageIndex.value < allImages.value.length - 1) currentImageIndex.value++;
};

const handleAddPhotoInput = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  target.value = '';

  isAddingPhoto.value = true;
  try {
    await addReceiptImage(props.receipt.id, file);
    currentImageIndex.value = allImages.value.length - 1;
    toast.add({ title: 'Dodano zdjęcie', color: 'green' });
  } catch (error) {
    toast.add({
      title: 'Błąd',
      description: error instanceof Error ? error.message : 'Nie udało się dodać zdjęcia',
      color: 'red',
    });
  } finally {
    isAddingPhoto.value = false;
  }
};

const { confirm } = useConfirm()

const handleVerify = async () => {
  if (!await confirm({ message: 'Mark this receipt as verified?', confirmText: 'Verify', variant: 'primary' })) return;

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
watch(() => props.receipt.id, () => { currentImageIndex.value = 0; });

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
    <!-- Image Gallery -->
    <div class="space-y-2">
      <div class="relative group">
        <div class="relative h-64 bg-card-black border border-border-gray rounded-lg overflow-hidden">
          <img
            :src="currentImageUrl"
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
          <!-- Prev/Next buttons -->
          <button
            v-if="currentImageIndex > 0"
            class="absolute left-2 top-1/2 -translate-y-1/2 p-1.5 bg-background-black/70 rounded-full text-pure-white hover:bg-background-black transition-colors"
            @click.stop="prevImage"
          >
            <UIcon name="i-heroicons-chevron-left" class="w-5 h-5" />
          </button>
          <button
            v-if="currentImageIndex < allImages.length - 1"
            class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-background-black/70 rounded-full text-pure-white hover:bg-background-black transition-colors"
            @click.stop="nextImage"
          >
            <UIcon name="i-heroicons-chevron-right" class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Image counter + Add Photo -->
      <div class="flex items-center justify-between">
        <span v-if="allImages.length > 1" class="text-xs text-pure-white/50">
          {{ currentImageIndex + 1 }} / {{ allImages.length }}
        </span>
        <span v-else />

        <div class="flex items-center gap-2">
          <!-- Dot indicators -->
          <div v-if="allImages.length > 1" class="flex gap-1">
            <button
              v-for="(_, i) in allImages"
              :key="i"
              class="w-2 h-2 rounded-full transition-colors"
              :class="i === currentImageIndex ? 'bg-cyber-blue' : 'bg-border-gray'"
              @click="currentImageIndex = i"
            />
          </div>

          <!-- Add Photo button -->
          <input
            ref="addPhotoInputRef"
            type="file"
            accept="image/*"
            class="absolute w-px h-px opacity-0 overflow-hidden"
            @change="handleAddPhotoInput"
          />
          <BaseButton
            variant="ghost"
            size="sm"
            icon="i-heroicons-camera-plus"
            :loading="isAddingPhoto"
            @click="addPhotoInputRef?.click()"
          >
            Dodaj zdjęcie
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Basic Info -->
    <div class="grid grid-cols-2 gap-4">
      <div>
        <p class="text-sm font-medium text-pure-white/60">Merchant</p>
        <p class="mt-1 text-base font-semibold text-pure-white">
          {{ receipt.merchant || "Unknown" }}
        </p>
      </div>
      <div>
        <p class="text-sm font-medium text-pure-white/60">Date</p>
        <p class="mt-1 text-base font-semibold text-pure-white">
          {{ formatDate(receipt.scan_date) }}
        </p>
      </div>
      <div>
        <p class="text-sm font-medium text-pure-white/60">Total</p>
        <p class="mt-1 text-base font-semibold text-electric-green">
          {{ receipt.total ? formatCurrency(receipt.total) : "N/A" }}
        </p>
      </div>
      <div>
        <p class="text-sm font-medium text-pure-white/60">Status</p>
        <div class="mt-1">
          <UBadge
            :color="receipt.verified ? 'success' : 'warning'"
            variant="solid"
            size="sm"
          >
            {{ receipt.verified ? "Verified" : "Pending" }}
          </UBadge>
        </div>
      </div>
    </div>

    <!-- Verify Button -->
    <BaseButton
      v-if="!receipt.verified"
      size="sm"
      variant="primary"
      icon="i-heroicons-check"
      :loading="isVerifying"
      class="w-full"
      @click="handleVerify"
    >
      Mark as Verified
    </BaseButton>

    <!-- Items -->
    <div v-if="items.length > 0">
      <h3 class="text-lg font-semibold text-pure-white mb-3">Items</h3>

      <!-- Mobile: Cards View (< 1024px) -->
      <div class="space-y-3 lg:hidden">
        <ReceiptItemCard
          v-for="(item, index) in items"
          :key="index"
          :item="item"
          :index="index"
          :is-editable="!updatingItems"
          @update="(updatedItem) => handleItemUpdate(index, updatedItem)"
        />
        <!-- Mobile Subtotal -->
        <div class="bg-card-black/50 border border-border-gray rounded-lg p-4 flex justify-between items-center">
          <span class="font-semibold text-pure-white">Subtotal</span>
          <span class="font-semibold text-electric-green">{{ formatCurrency(itemsTotal) }}</span>
        </div>
      </div>

      <!-- Desktop: Table View (≥ 1024px) -->
      <div class="hidden lg:block border border-border-gray rounded-lg overflow-hidden">
        <table class="min-w-full divide-y divide-border-gray">
          <thead class="bg-card-black/50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                Item
              </th>
              <th class="px-4 py-3 text-right text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                Qty
              </th>
              <th class="px-4 py-3 text-right text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                Unit Price
              </th>
              <th class="px-4 py-3 text-right text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                Total
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-pure-white/60 uppercase tracking-wider">
                Category
              </th>
              <th class="px-4 py-3 text-right text-xs font-medium text-pure-white/60 uppercase tracking-wider">
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
              <td colspan="3" class="px-4 py-3 text-sm text-pure-white text-right">
                Subtotal
              </td>
              <td class="px-4 py-3 text-sm text-electric-green text-right">
                {{ formatCurrency(itemsTotal) }}
              </td>
              <td colspan="2"></td>
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
      :image-url="currentImageUrl"
      :title="`Receipt from ${receipt.merchant || 'Unknown'}`"
    />
  </div>
</template>
