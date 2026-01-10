/**
 * Receipt management composable
 * Handles receipt upload, OCR processing, and CRUD
 * Supports household context via optional householdId parameter
 */

import type { Receipt, ReceiptUpdate } from "~/types/api";
import { buildQueryParams } from "./useApi";

export const useReceipts = () => {
  const api = useApi();
  const receipts = ref<Receipt[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch all receipts
   * @param householdId - Optional household context
   */
  const fetchReceipts = async (householdId?: string | null): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      const data = await api<Receipt[]>(`/api/v1/receipts${queryString}`);
      receipts.value = data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Failed to fetch receipts";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Fetch single receipt by ID
   * @param id - Receipt ID
   * @param householdId - Optional household context
   */
  const fetchReceipt = async (
    id: number,
    householdId?: string | null
  ): Promise<Receipt> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      const data = await api<Receipt>(`/api/v1/receipts/${id}${queryString}`);
      return data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Failed to fetch receipt";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Upload and process receipt image with optional OCR
   * @param file - Image file to upload
   * @param geminiApiKey - Optional Gemini API key for OCR
   * @param householdId - Optional household to assign receipt to
   */
  const uploadReceipt = async (
    file: File,
    geminiApiKey?: string,
    householdId?: string | null
  ): Promise<Receipt> => {
    loading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      formData.append("file", file);

      if (geminiApiKey) {
        formData.append("gemini_api_key", geminiApiKey);
      }

      const queryString = buildQueryParams({}, householdId);
      const data = await api<Receipt>(`/api/v1/receipts/upload${queryString}`, {
        method: "POST",
        body: formData,
      });

      receipts.value.unshift(data);
      return data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Failed to upload receipt";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Update receipt metadata
   * @param id - Receipt ID
   * @param updates - Fields to update
   * @param householdId - Optional household context
   */
  const updateReceipt = async (
    id: number,
    updates: ReceiptUpdate,
    householdId?: string | null
  ): Promise<Receipt> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      const data = await api<Receipt>(`/api/v1/receipts/${id}${queryString}`, {
        method: "PUT",
        body: updates,
      });

      const index = receipts.value.findIndex((r) => r.id === id);
      if (index !== -1) {
        receipts.value[index] = data;
      }

      return data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Failed to update receipt";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Delete receipt
   * @param id - Receipt ID
   * @param householdId - Optional household context
   */
  const deleteReceipt = async (
    id: number,
    householdId?: string | null
  ): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      await api(`/api/v1/receipts/${id}${queryString}`, {
        method: "DELETE",
      });

      receipts.value = receipts.value.filter((r) => r.id !== id);
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Failed to delete receipt";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Get receipt image URL
   * Returns relative URL that goes through Nuxt server proxy
   */
  const getReceiptImageUrl = (imagePath: string): string => {
    // imagePath is just the filename (e.g., "uuid.jpeg")
    // Return relative URL - Nuxt server proxy will forward to backend
    // Backend serves images at GET /api/v1/receipts/images/{filename}
    return `/api/v1/receipts/images/${imagePath}`;
  };

  /**
   * Mark receipt as verified
   * @param id - Receipt ID
   * @param householdId - Optional household context
   */
  const verifyReceipt = async (
    id: number,
    householdId?: string | null
  ): Promise<Receipt> => {
    return updateReceipt(id, { verified: true }, householdId);
  };

  /**
   * Update receipt category
   * @param id - Receipt ID
   * @param category - New category name
   * @param householdId - Optional household context
   */
  const updateReceiptCategory = async (
    id: number,
    category: string,
    householdId?: string | null
  ): Promise<Receipt> => {
    return updateReceipt(id, { category }, householdId);
  };

  return {
    receipts,
    loading,
    error,
    fetchReceipts,
    fetchReceipt,
    uploadReceipt,
    updateReceipt,
    deleteReceipt,
    verifyReceipt,
    updateReceiptCategory,
    getReceiptImageUrl,
  };
};
