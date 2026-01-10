/**
 * Analytics Composable
 *
 * Provides functions to fetch financial analytics data from the backend.
 * Supports household context via optional householdId parameter.
 * Includes household-specific analytics endpoints.
 */

import type {
  MonthSummary,
  YearlySummary,
  CategorySpending,
  MerchantSpending,
  SpendingTrend,
  BudgetStatus,
  BudgetSettings,
  BudgetSettingsUpdate,
  CompleteBudgetStatus,
  BudgetAlertsResponse,
  HouseholdMonthlySummary,
  HouseholdSpendingByMember,
  HouseholdSpendingByCategory,
} from '~/types/api'
import { buildQueryParams } from './useApi'

export function useAnalytics() {
  const api = useApi()

  // ============================================
  // Personal Analytics (with optional household context)
  // ============================================

  /**
   * Get monthly summary with income, expenses, and category breakdown
   * @param month - Month in YYYY-MM format
   * @param householdId - Optional household context
   */
  const getMonthlySummary = async (
    month: string,
    householdId?: string | null
  ): Promise<MonthSummary> => {
    try {
      const queryString = buildQueryParams({ month }, householdId)
      const response = await api<MonthSummary>(`/api/v1/analytics/summary${queryString}`)
      return response
    } catch (error) {
      console.error('Failed to fetch monthly summary:', error)
      throw error
    }
  }

  /**
   * Get yearly summary with monthly breakdown
   * @param year - Year in YYYY format
   * @param householdId - Optional household context
   */
  const getYearlySummary = async (
    year: string,
    householdId?: string | null
  ): Promise<YearlySummary> => {
    try {
      const queryString = buildQueryParams({ year }, householdId)
      const response = await api<YearlySummary>(`/api/v1/analytics/yearly-summary${queryString}`)
      return response
    } catch (error) {
      console.error('Failed to fetch yearly summary:', error)
      throw error
    }
  }

  /**
   * Get spending breakdown by category
   * @param month - Optional month filter in YYYY-MM format
   * @param householdId - Optional household context
   */
  const getSpendingByCategory = async (
    month?: string,
    householdId?: string | null
  ): Promise<CategorySpending[]> => {
    try {
      const queryString = buildQueryParams({ month: month || null }, householdId)
      const response = await api<CategorySpending[]>(`/api/v1/analytics/by-category${queryString}`)
      return response
    } catch (error) {
      console.error('Failed to fetch spending by category:', error)
      throw error
    }
  }

  /**
   * Get spending breakdown by merchant/shop
   * @param month - Optional month filter in YYYY-MM format
   * @param householdId - Optional household context
   */
  const getSpendingByMerchant = async (
    month?: string,
    householdId?: string | null
  ): Promise<MerchantSpending[]> => {
    try {
      const queryString = buildQueryParams({ month: month || null }, householdId)
      const response = await api<MerchantSpending[]>(`/api/v1/analytics/by-merchant${queryString}`)
      return response
    } catch (error) {
      console.error('Failed to fetch spending by merchant:', error)
      throw error
    }
  }

  /**
   * Get top N transactions (expenses or income)
   * @param limit - Number of transactions to return
   * @param type - Type of transactions to return
   * @param month - Optional month filter
   * @param category - Optional category filter
   * @param householdId - Optional household context
   */
  const getTopTransactions = async (
    limit: number = 10,
    type: 'expenses' | 'income' = 'expenses',
    month?: string,
    category?: string,
    householdId?: string | null
  ) => {
    try {
      const queryString = buildQueryParams(
        { limit, type, month: month || null, category: category || null },
        householdId
      )
      const response = await api(`/api/v1/analytics/top${queryString}`)
      return response
    } catch (error) {
      console.error('Failed to fetch top transactions:', error)
      throw error
    }
  }

  /**
   * Get spending trends over time
   * @param months - Number of months to include
   * @param category - Optional category filter
   * @param householdId - Optional household context
   */
  const getSpendingTrends = async (
    months: number = 6,
    category?: string,
    householdId?: string | null
  ): Promise<SpendingTrend[]> => {
    try {
      const queryString = buildQueryParams(
        { months, category: category || null },
        householdId
      )
      const response = await api<SpendingTrend[]>(`/api/v1/analytics/trends${queryString}`)
      return response
    } catch (error) {
      console.error('Failed to fetch spending trends:', error)
      throw error
    }
  }

  /**
   * Get budget status for all categories with limits
   * @param month - Month in YYYY-MM format
   * @param householdId - Optional household context
   */
  const getBudgetStatus = async (
    month: string,
    householdId?: string | null
  ): Promise<BudgetStatus[]> => {
    try {
      const queryString = buildQueryParams({ month }, householdId)
      const response = await api<BudgetStatus[]>(`/api/v1/analytics/budget-status${queryString}`)
      return response
    } catch (error) {
      console.error('Failed to fetch budget status:', error)
      throw error
    }
  }

  /**
   * Get budget settings
   * @param householdId - Optional household context
   */
  const getBudgetSettings = async (householdId?: string | null): Promise<BudgetSettings> => {
    try {
      const queryString = buildQueryParams({}, householdId)
      const response = await api<BudgetSettings>(`/api/v1/analytics/budget-settings${queryString}`)
      return response
    } catch (error) {
      console.error('Failed to fetch budget settings:', error)
      throw error
    }
  }

  /**
   * Update budget settings
   * @param settings - Settings to update
   * @param householdId - Optional household context
   */
  const updateBudgetSettings = async (
    settings: BudgetSettingsUpdate,
    householdId?: string | null
  ): Promise<BudgetSettings> => {
    try {
      const queryString = buildQueryParams({}, householdId)
      const response = await api<BudgetSettings>(`/api/v1/analytics/budget-settings${queryString}`, {
        method: 'PUT',
        body: settings,
      })
      return response
    } catch (error) {
      console.error('Failed to update budget settings:', error)
      throw error
    }
  }

  /**
   * Get complete budget status (overall + categories)
   * @param month - Month in YYYY-MM format
   * @param householdId - Optional household context
   */
  const getCompleteBudgetStatus = async (
    month: string,
    householdId?: string | null
  ): Promise<CompleteBudgetStatus> => {
    try {
      const queryString = buildQueryParams({ month }, householdId)
      const response = await api<CompleteBudgetStatus>(
        `/api/v1/analytics/budget-status-complete${queryString}`
      )
      return response
    } catch (error) {
      console.error('Failed to fetch complete budget status:', error)
      throw error
    }
  }

  /**
   * Check for budget alerts
   * @param month - Month in YYYY-MM format
   * @param householdId - Optional household context
   */
  const checkBudgetAlerts = async (
    month: string,
    householdId?: string | null
  ): Promise<BudgetAlertsResponse> => {
    try {
      const queryString = buildQueryParams({ month }, householdId)
      const response = await api<BudgetAlertsResponse>(
        `/api/v1/analytics/budget-alerts${queryString}`
      )
      return response
    } catch (error) {
      console.error('Failed to check budget alerts:', error)
      throw error
    }
  }

  // ============================================
  // Household-specific Analytics
  // ============================================

  /**
   * Get household monthly summary
   * @param householdUid - Household UUID
   * @param month - Month in YYYY-MM format
   */
  const getHouseholdMonthlySummary = async (
    householdUid: string,
    month: string
  ): Promise<HouseholdMonthlySummary> => {
    try {
      const response = await api<HouseholdMonthlySummary>(
        `/api/v1/households/${householdUid}/analytics/summary?month=${month}`
      )
      return response
    } catch (error) {
      console.error('Failed to fetch household monthly summary:', error)
      throw error
    }
  }

  /**
   * Get household spending breakdown by member
   * @param householdUid - Household UUID
   * @param month - Optional month filter in YYYY-MM format
   */
  const getHouseholdSpendingByMember = async (
    householdUid: string,
    month?: string
  ): Promise<HouseholdSpendingByMember> => {
    try {
      const query = month ? `?month=${month}` : ''
      const response = await api<HouseholdSpendingByMember>(
        `/api/v1/households/${householdUid}/analytics/by-member${query}`
      )
      return response
    } catch (error) {
      console.error('Failed to fetch household spending by member:', error)
      throw error
    }
  }

  /**
   * Get household spending by category with member breakdown
   * @param householdUid - Household UUID
   * @param month - Optional month filter in YYYY-MM format
   */
  const getHouseholdSpendingByCategory = async (
    householdUid: string,
    month?: string
  ): Promise<HouseholdSpendingByCategory> => {
    try {
      const query = month ? `?month=${month}` : ''
      const response = await api<HouseholdSpendingByCategory>(
        `/api/v1/households/${householdUid}/analytics/by-category${query}`
      )
      return response
    } catch (error) {
      console.error('Failed to fetch household spending by category:', error)
      throw error
    }
  }

  return {
    // Personal analytics
    getMonthlySummary,
    getYearlySummary,
    getSpendingByCategory,
    getSpendingByMerchant,
    getTopTransactions,
    getSpendingTrends,
    getBudgetStatus,
    getBudgetSettings,
    updateBudgetSettings,
    getCompleteBudgetStatus,
    checkBudgetAlerts,
    // Household analytics
    getHouseholdMonthlySummary,
    getHouseholdSpendingByMember,
    getHouseholdSpendingByCategory,
  }
}
