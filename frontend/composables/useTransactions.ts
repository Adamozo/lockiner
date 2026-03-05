/**
 * Transaction management composable
 * Handles CRUD operations for transactions
 * Supports household context via optional householdId parameter
 */

import type {
  Transaction,
  TransactionCreate,
  TransactionUpdate,
  DateRange,
  PaginationParams,
} from "~/types/api";
import { buildQueryParams } from "./useApi";

interface TransactionFilters extends DateRange, PaginationParams {
  householdId?: string | null;
}

export const useTransactions = () => {
  const api = useApi();
  const transactions = ref<Transaction[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Build URL with query params including optional household_id
   */
  const buildUrl = (
    base: string,
    filters?: TransactionFilters
  ): string => {
    const queryString = buildQueryParams(
      {
        start_date: filters?.start_date,
        end_date: filters?.end_date,
        skip: filters?.skip,
        limit: filters?.limit,
      },
      filters?.householdId
    );
    return `${base}${queryString}`;
  };

  /**
   * Fetch all transactions with optional filters
   * @param filters - Optional filters including householdId for household context
   */
  const fetchTransactions = async (
    filters?: TransactionFilters
  ): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      const url = buildUrl("/api/v1/transactions", filters);
      const data = await api<Transaction[]>(url);
      transactions.value = data;
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Failed to fetch transactions";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Fetch single transaction by ID
   * @param id - Transaction ID
   * @param householdId - Optional household context
   */
  const fetchTransaction = async (
    id: number,
    householdId?: string | null
  ): Promise<Transaction> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      const data = await api<Transaction>(`/api/v1/transactions/${id}${queryString}`);
      return data;
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Failed to fetch transaction";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Create new transaction
   * @param transaction - Transaction data
   * @param householdId - Optional household to assign transaction to
   */
  const createTransaction = async (
    transaction: TransactionCreate,
    householdId?: string | null
  ): Promise<Transaction> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      const data = await api<Transaction>(`/api/v1/transactions${queryString}`, {
        method: "POST",
        body: transaction,
      });

      // Add to local state
      transactions.value.unshift(data);

      return data;
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Failed to create transaction";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Update existing transaction
   * @param id - Transaction ID
   * @param updates - Fields to update
   * @param householdId - Optional household context
   */
  const updateTransaction = async (
    id: number,
    updates: TransactionUpdate,
    householdId?: string | null
  ): Promise<Transaction> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      const data = await api<Transaction>(`/api/v1/transactions/${id}${queryString}`, {
        method: "PUT",
        body: updates,
      });

      // Update local state
      const index = transactions.value.findIndex((t) => t.id === id);
      if (index !== -1) {
        transactions.value[index] = data;
      }

      return data;
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Failed to update transaction";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Delete transaction
   * @param id - Transaction ID
   * @param householdId - Optional household context
   */
  const deleteTransaction = async (
    id: number,
    householdId?: string | null
  ): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      const queryString = buildQueryParams({}, householdId);
      await api(`/api/v1/transactions/${id}${queryString}`, {
        method: "DELETE",
      });

      // Remove from local state
      transactions.value = transactions.value.filter((t) => t.id !== id);
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Failed to delete transaction";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Import transactions from CSV
   * @param file - CSV file to import
   * @param householdId - Optional household to assign imported transactions to
   */
  const importCSV = async (
    file: File,
    householdId?: string | null
  ): Promise<{ imported: number; failed: number }> => {
    loading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      formData.append("file", file);

      const queryString = buildQueryParams({}, householdId);
      const data = await api<{ imported: number; failed: number }>(
        `/api/v1/transactions/import-csv${queryString}`,
        {
          method: "POST",
          body: formData,
        }
      );

      // Refresh transactions after import
      await fetchTransactions({ householdId });

      return data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Failed to import CSV";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  const bulkDeleteTransactions = async (
    ids: number[],
    householdId?: string | null
  ): Promise<{ deleted: number }> => {
    loading.value = true;
    error.value = null;
    try {
      const queryString = buildQueryParams({}, householdId);
      const data = await api<{ deleted: number }>(
        `/api/v1/transactions/bulk-delete${queryString}`,
        { method: "POST", body: { ids } }
      );
      await fetchTransactions({ householdId });
      return data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Failed to delete transactions";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  const importBankPDF = async (
    file: File,
    bank: string,
    householdId?: string | null
  ): Promise<{ imported: number; failed: number; errors: string[] }> => {
    loading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      formData.append("file", file);

      const queryString = buildQueryParams({ bank }, householdId);
      const data = await api<{ imported: number; failed: number; errors: string[] }>(
        `/api/v1/transactions/import-pdf${queryString}`,
        { method: "POST", body: formData }
      );

      await fetchTransactions({ householdId });
      return data;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Failed to import PDF";
      throw e;
    } finally {
      loading.value = false;
    }
  };

  return {
    transactions,
    loading,
    error,
    fetchTransactions,
    fetchTransaction,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    importCSV,
    importBankPDF,
    bulkDeleteTransactions,
  };
};
