/**
 * Utility functions for formatting data
 */

/**
 * Format number as Polish currency (PLN)
 * @param amount - Amount to format
 * @returns Formatted currency string (e.g., "1 234,56 zł")
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
  }).format(amount)
}

/**
 * Format date string to Polish locale
 * @param dateString - ISO date string (YYYY-MM-DD or ISO 8601)
 * @returns Formatted date string (e.g., "10.01.2026")
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date)
}

/**
 * Format datetime string to Polish locale with time
 * @param dateString - ISO 8601 datetime string
 * @returns Formatted datetime string (e.g., "10.01.2026, 15:30")
 */
export function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

/**
 * Format date for HTML input[type="date"]
 * @param date - Date object or ISO string
 * @returns YYYY-MM-DD string
 */
export function formatDateForInput(date: Date | string = new Date()): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toISOString().split('T')[0]
}

/**
 * Get relative time string (e.g., "2 days ago", "in 3 hours")
 * @param dateString - ISO date string
 * @returns Relative time string
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return 'Dzisiaj'
  } else if (diffDays === 1) {
    return 'Wczoraj'
  } else if (diffDays === -1) {
    return 'Jutro'
  } else if (diffDays > 1 && diffDays < 7) {
    return `${diffDays} dni temu`
  } else if (diffDays < -1 && diffDays > -7) {
    return `Za ${Math.abs(diffDays)} dni`
  } else {
    return formatDate(dateString)
  }
}

/**
 * Format transaction amount with color indicator
 * @param amount - Transaction amount (negative = expense)
 * @returns Object with formatted value and CSS class
 */
export function formatTransactionAmount(amount: number): {
  text: string
  class: string
} {
  const isIncome = amount > 0
  return {
    text: formatCurrency(Math.abs(amount)),
    class: isIncome ? 'text-green-600' : 'text-red-600',
  }
}

/**
 * Truncate text to specified length
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @returns Truncated text with ellipsis
 */
export function truncateText(text: string | null, maxLength: number = 50): string {
  if (!text) return ''
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
}

/**
 * Calculate percentage
 * @param value - Part value
 * @param total - Total value
 * @returns Percentage with 1 decimal place
 */
export function calculatePercentage(value: number, total: number): string {
  if (total === 0) return '0.0%'
  return ((value / total) * 100).toFixed(1) + '%'
}
