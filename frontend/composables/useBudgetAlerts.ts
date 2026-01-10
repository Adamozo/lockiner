/**
 * Budget Alerts Composable
 *
 * Manages budget alert notifications and checking
 */

import type { BudgetAlert } from '~/types/api'

export function useBudgetAlerts() {
  const { checkBudgetAlerts } = useAnalytics()
  const toast = useToast()

  // State for active alerts
  const activeAlerts = ref<BudgetAlert[]>([])
  const hasUnreadAlerts = ref(false)

  /**
   * Check and display budget alerts for a given month
   * @param month - Month in YYYY-MM format
   * @param showToast - Whether to show toast notifications
   * @param householdId - Optional household context
   */
  const checkAndDisplayAlerts = async (
    month: string,
    showToast = true,
    householdId?: string | null
  ) => {
    try {
      const response = await checkBudgetAlerts(month, householdId)
      activeAlerts.value = response.alerts
      hasUnreadAlerts.value = response.alerts.length > 0

      // Show toast notifications if enabled
      if (showToast && response.alerts.length > 0) {
        response.alerts.forEach((alert) => {
          toast.add({
            title: alert.type === 'overall' ? 'Budget Alert' : `${alert.category} Budget`,
            description: alert.message,
            color: alert.severity === 'over' ? 'red' : 'orange',
            icon:
              alert.icon
                ? undefined
                : alert.severity === 'over'
                ? 'i-heroicons-exclamation-circle'
                : 'i-heroicons-exclamation-triangle',
          })
        })
      }

      return response.alerts
    } catch (error) {
      console.error('Failed to check budget alerts:', error)
      return []
    }
  }

  /**
   * Mark alerts as read
   */
  const markAlertsAsRead = () => {
    hasUnreadAlerts.value = false
  }

  /**
   * Get alert count
   */
  const alertCount = computed(() => activeAlerts.value.length)

  /**
   * Get alerts by severity
   */
  const criticalAlerts = computed(() => activeAlerts.value.filter((a) => a.severity === 'over'))

  const warningAlerts = computed(() => activeAlerts.value.filter((a) => a.severity === 'warning'))

  return {
    activeAlerts,
    hasUnreadAlerts,
    alertCount,
    criticalAlerts,
    warningAlerts,
    checkAndDisplayAlerts,
    markAlertsAsRead,
  }
}
