/**
 * Category management composable
 * Handles category CRUD operations and caching
 * Supports household context via optional householdId parameter
 */

import type { Category, CategoryCreate } from "~/types/api";
import { buildQueryParams } from "./useApi";

export const useCategories = () => {
  const api = useApi();
  const categories = ref<Category[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch all categories
   * @param householdId - Optional household context (includes household + default categories)
   */
  const fetchCategories = async (householdId?: string | null): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      const data = await api<Category[]>(`/api/v1/categories/${queryString}`);
      categories.value = data;
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Failed to fetch categories";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Create new category
   * @param category - Category data
   * @param householdId - Optional household to assign category to
   */
  const createCategory = async (
    category: CategoryCreate,
    householdId?: string | null
  ): Promise<Category> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      const data = await api<Category>(`/api/v1/categories/${queryString}`, {
        method: "POST",
        body: category,
      });

      categories.value.push(data);
      return data;
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Failed to create category";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Update category
   * @param id - Category ID
   * @param updates - Fields to update
   * @param householdId - Optional household context
   */
  const updateCategory = async (
    id: number,
    updates: Partial<CategoryCreate>,
    householdId?: string | null
  ): Promise<Category> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      const data = await api<Category>(`/api/v1/categories/${id}${queryString}`, {
        method: "PUT",
        body: updates,
      });

      const index = categories.value.findIndex((c) => c.id === id);
      if (index !== -1) {
        categories.value[index] = data;
      }

      return data;
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Failed to update category";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Delete category
   * @param id - Category ID
   * @param householdId - Optional household context
   */
  const deleteCategory = async (
    id: number,
    householdId?: string | null
  ): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      await api(`/api/v1/categories/${id}${queryString}`, {
        method: "DELETE",
      });

      categories.value = categories.value.filter((c) => c.id !== id);
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Failed to delete category";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Get category names for dropdown/select
   */
  const categoryNames = computed(() => {
    return categories.value.map((c) => c.name);
  });

  /**
   * Get category by name
   */
  const getCategoryByName = (name: string): Category | undefined => {
    return categories.value.find((c) => c.name === name);
  };

  return {
    categories,
    categoryNames,
    loading,
    error,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    getCategoryByName,
  };
};
