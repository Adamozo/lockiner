// API Types for LockIner Backend

/**
 * Transaction - Core financial transaction model
 */
export interface Transaction {
  id: number
  date: string // ISO 8601: YYYY-MM-DD
  amount: number // Negative = expense, Positive = income
  description: string | null
  category: string
  payment_method: string | null // card, cash, blik, other
  receipt_id: number | null
  notes: string | null
  created_at: string // ISO 8601 datetime
}

/**
 * TransactionCreate - Create new transaction
 */
export interface TransactionCreate {
  date: string // YYYY-MM-DD
  amount: number
  description?: string | null
  category?: string
  payment_method?: string | null
  notes?: string | null
}

/**
 * TransactionUpdate - Update existing transaction
 */
export interface TransactionUpdate {
  date?: string
  amount?: number
  description?: string | null
  category?: string
  payment_method?: string | null
  notes?: string | null
  receipt_id?: number | null
}

/**
 * Receipt - OCR scanned receipt
 */
export interface Receipt {
  id: number
  image_path: string
  scan_date: string // ISO 8601
  merchant: string | null
  total: number | null
  payment_method: string | null
  items_json: string | null // JSON string of items array
  raw_ocr_response: string | null
  verified: boolean
  category: string
  created_at: string
}

/**
 * ReceiptCreate - Upload new receipt
 */
export interface ReceiptCreate {
  merchant?: string | null
  total?: number | null
  verified?: boolean
}

/**
 * ReceiptItem - Parsed receipt item
 */
export interface ReceiptItem {
  name: string
  quantity: number
  unit_price: number
  total_price: number
  category?: string // Optional item-level category (defaults to receipt category)
}

/**
 * Category - Transaction category
 */
export interface Category {
  id: number
  name: string
  budget_limit: number | null
  icon: string | null
  color: string | null
}

/**
 * CategoryCreate - Create new category
 */
export interface CategoryCreate {
  name: string
  budget_limit?: number | null
  icon?: string | null
  color?: string | null
}

/**
 * AnalyticsSummary - Financial analytics
 */
export interface AnalyticsSummary {
  total_income: number
  total_expenses: number
  balance: number
  transactions_count: number
  categories: CategorySummary[]
}

/**
 * CategorySummary - Category spending summary
 */
export interface CategorySummary {
  category: string
  total: number
  count: number
  percentage?: number // Calculated on frontend
}

/**
 * DateRange - Query parameter for filtering by date
 */
export interface DateRange {
  start_date?: string // YYYY-MM-DD
  end_date?: string // YYYY-MM-DD
}

/**
 * PaginationParams - Query parameters for pagination
 */
export interface PaginationParams {
  skip?: number
  limit?: number
}

/**
 * APIError - Standard error response
 */
export interface APIError {
  detail: string
}

/**
 * CSVImportResult - CSV import response
 */
export interface CSVImportResult {
  imported: number
  failed: number
  errors: string[]
}

/**
 * OCRResponse - Response from OCR processing
 */
export interface OCRResponse {
  merchant: string
  date: string // YYYY-MM-DD
  total: number
  payment_method: string // karta, gotówka, blik
  items: ReceiptItem[]
  tax_amount: number
  currency: string
}

/**
 * ReceiptUploadResult - Response from upload endpoint
 */
export interface ReceiptUploadResult {
  receipt_id: number
  image_path: string
  ocr_data: OCRResponse | null
  error: string | null
  created_at: string
}

/**
 * ReceiptUpdate - Update receipt data
 */
export interface ReceiptUpdate {
  merchant?: string | null
  total?: number | null
  payment_method?: string | null
  items_json?: string | null
  verified?: boolean
  category?: string
}

/**
 * GeminiKeyStatus - API key configuration status
 */
export interface GeminiKeyStatus {
  configured: boolean
}

/**
 * GeminiKeyRequest - Request to save Gemini API key
 */
export interface GeminiKeyRequest {
  api_key: string
}

/**
 * CategorySpending - Category spending analytics
 */
export interface CategorySpending {
  category: string
  total: number
  count: number
  average: number
  percentage?: number
}

/**
 * MonthSummary - Monthly spending summary
 */
export interface MonthSummary {
  month: string // YYYY-MM
  total_income: number
  total_expenses: number
  net_amount: number
  transactions_count: number
  by_category: CategorySpending[]
}

/**
 * YearlySummary - Yearly spending summary
 */
export interface YearlySummary {
  year: string // YYYY
  total_income: number
  total_expenses: number
  net_amount: number
  transactions_count: number
  receipts_count: number
  by_category: CategorySpending[]
  monthly_breakdown: MonthSummary[]
}

/**
 * MerchantSpending - Merchant/shop spending analytics
 */
export interface MerchantSpending {
  merchant: string
  total: number
  receipts_count: number
  average: number
  percentage?: number
}

/**
 * SpendingTrend - Spending trend over time
 */
export interface SpendingTrend {
  month: string // YYYY-MM
  amount: number
}

/**
 * BudgetStatus - Budget status for a category
 */
export interface BudgetStatus {
  category: string
  icon: string
  color: string
  budget_limit: number
  spent: number
  remaining: number
  percentage: number
  status: 'ok' | 'warning' | 'over'
}

/**
 * BudgetSettings - Global budget configuration
 */
export interface BudgetSettings {
  id: number
  overall_monthly_limit: number | null
  alert_threshold_warning: number
  alert_threshold_danger: number
  enable_alerts: boolean
  created_at: string
  updated_at: string | null
}

/**
 * BudgetSettingsUpdate - Update budget settings
 */
export interface BudgetSettingsUpdate {
  overall_monthly_limit?: number | null
  alert_threshold_warning?: number
  alert_threshold_danger?: number
  enable_alerts?: boolean
}

/**
 * OverallBudgetStatus - Overall budget status for a month
 */
export interface OverallBudgetStatus {
  month: string
  overall_limit: number | null
  total_spent: number
  remaining: number
  percentage: number
  status: 'ok' | 'warning' | 'over' | 'no_limit'
  alert_message: string | null
}

/**
 * CompleteBudgetStatus - Complete budget status
 */
export interface CompleteBudgetStatus {
  overall: OverallBudgetStatus
  categories: BudgetStatus[]
  settings: BudgetSettings
}

/**
 * BudgetAlert - Budget alert notification
 */
export interface BudgetAlert {
  type: 'overall' | 'category'
  severity: 'warning' | 'over'
  message: string
  category: string | null
  icon?: string
  color?: string
}

/**
 * BudgetAlertsResponse - Budget alerts response
 */
export interface BudgetAlertsResponse {
  alerts: BudgetAlert[]
}

// ============================================
// Authentication Types (Phase 1)
// ============================================

/**
 * User - Authenticated user model
 */
export interface User {
  id: number
  email: string // Note: backend stores email_hash, but returns email for display
  name: string
  role: 'user' | 'admin'
  is_active: boolean
  totp_enabled: boolean
  created_at: string
  updated_at: string | null
  language: string
}

/**
 * UserCreate - Register new user
 */
export interface UserCreate {
  email: string
  password: string
  name: string
  voucher_code: string
  language?: string
}

/**
 * UserUpdate - Update user profile
 */
export interface UserUpdate {
  name?: string
  language?: string
}

/**
 * UserResponse - User data returned from API
 */
export interface UserResponse {
  id: number
  email: string
  name: string
  is_active: boolean
  created_at: string
  updated_at: string | null
}

/**
 * LoginRequest - Login credentials
 */
export interface LoginRequest {
  email: string
  password: string
}

/**
 * TokenResponse - JWT tokens returned after login
 */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string // "bearer"
}

/**
 * RefreshTokenRequest - Request to refresh access token
 */
export interface RefreshTokenRequest {
  refresh_token: string
}

/**
 * PasswordChangeRequest - Change password request
 */
export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

// ============================================
// Two-Factor Authentication Types
// ============================================

/**
 * LoginResponse - Extended login response supporting 2FA
 */
export interface LoginResponse {
  access_token?: string
  refresh_token?: string
  token_type: string
  expires_in?: number
  requires_2fa: boolean
  two_factor_token?: string
}

/**
 * TwoFactorSetupResponse - Response when initiating 2FA setup
 */
export interface TwoFactorSetupResponse {
  secret: string
  uri: string
}

/**
 * TwoFactorVerifySetupResponse - Recovery codes after 2FA setup
 */
export interface TwoFactorVerifySetupResponse {
  recovery_codes: string[]
}

/**
 * TwoFactorStatusResponse - Current 2FA status
 */
export interface TwoFactorStatusResponse {
  enabled: boolean
  recovery_codes_remaining: number
}

/**
 * TwoFactorRegenerateResponse - Regenerated recovery codes
 */
export interface TwoFactorRegenerateResponse {
  recovery_codes: string[]
}

// ============================================
// Household Types (Phase 3)
// ============================================

/**
 * MemberRole - Household member role
 */
export type MemberRole = 'manager' | 'member'

/**
 * MemberStatus - Household member status
 */
export type MemberStatus = 'active' | 'blocked'

/**
 * Household - Household model
 */
export interface Household {
  id: number
  uid: string // UUID
  name: string
  description: string | null
  icon: string | null
  created_at: string
  updated_at: string | null
}

/**
 * HouseholdCreate - Create new household
 */
export interface HouseholdCreate {
  name: string
  description?: string | null
  icon?: string | null
}

/**
 * HouseholdUpdate - Update household
 */
export interface HouseholdUpdate {
  name?: string
  description?: string | null
  icon?: string | null
}

/**
 * HouseholdMember - Household member info
 */
export interface HouseholdMember {
  id: number
  user_id: number
  user_name: string
  user_email: string
  role: MemberRole
  status: MemberStatus
  joined_at: string
}

/**
 * HouseholdResponse - Household basic response
 */
export interface HouseholdResponse {
  id: number
  uid: string
  name: string
  description: string | null
  icon: string | null
  created_at: string
  updated_at: string | null
}

/**
 * HouseholdDetailResponse - Household with members
 */
export interface HouseholdDetailResponse extends HouseholdResponse {
  members: HouseholdMember[]
}

/**
 * HouseholdMemberUpdate - Update member role/status
 */
export interface HouseholdMemberUpdate {
  role?: MemberRole
  status?: MemberStatus
}

// ============================================
// Invitation Types (Phase 4)
// ============================================

/**
 * InvitationCreate - Create invitation
 */
export interface InvitationCreate {
  expires_in_days?: number | null
  max_uses?: number | null
}

/**
 * InvitationResponse - Invitation info
 */
export interface InvitationResponse {
  id: number
  token: string
  household_id: number
  household_name: string
  created_by_name: string
  expires_at: string | null
  max_uses: number | null
  uses_count: number
  is_active: boolean
  created_at: string
}

/**
 * InvitationPreview - Public invitation preview (no auth required)
 */
export interface InvitationPreview {
  household_name: string
  household_icon: string | null
  created_by_name: string
  expires_at: string | null
  is_valid: boolean
}

/**
 * InvitationJoinResponse - Response after joining household
 */
export interface InvitationJoinResponse {
  message: string
  household: HouseholdResponse
}

// ============================================
// Household Analytics Types (Phase 7)
// ============================================

/**
 * MemberSpending - Individual member spending summary
 */
export interface MemberSpending {
  user_id: number
  user_name: string
  total: number
  count: number
  average: number
  percentage: number
}

/**
 * HouseholdCategoryMemberBreakdown - Category spending with member breakdown
 */
export interface HouseholdCategoryMemberBreakdown {
  category: string
  total: number
  count: number
  percentage: number
  by_member: MemberSpending[]
}

/**
 * HouseholdMonthlySummary - Household monthly summary
 */
export interface HouseholdMonthlySummary {
  month: string // YYYY-MM
  total_income: number
  total_expenses: number
  net_amount: number
  transactions_count: number
  by_category: CategorySpending[]
  by_member: MemberSpending[]
}

/**
 * HouseholdSpendingByMember - Spending breakdown by member
 */
export interface HouseholdSpendingByMember {
  month: string | null // null = all-time
  members: MemberSpending[]
  total: number
}

/**
 * HouseholdSpendingByCategory - Category spending with member contributions
 */
export interface HouseholdSpendingByCategory {
  month: string | null
  categories: HouseholdCategoryMemberBreakdown[]
  total: number
}

// ============================================
// Notification Types
// ============================================

/**
 * NotificationItem - User notification from API
 */
export interface NotificationItem {
  id: number // user_notification.id
  notification_id: number
  title: string
  body: string
  notification_type: string
  status: 'unread' | 'read'
  read_at: string | null
  created_at: string
}

/**
 * UnreadCountResponse - Unread count
 */
export interface UnreadCountResponse {
  count: number
}

/**
 * DevicePushSubscription - Active push subscription for a user device
 */
export interface DevicePushSubscription {
  id: number
  endpoint: string
  created_at: string
}

// ============================================
// Admin Types
// ============================================

/**
 * VoucherAdmin - Admin voucher view
 */
export interface VoucherAdmin {
  id: number
  code: string
  status: 'available' | 'used' | 'blocked'
  used_by_user_id: number | null
  used_by_name: string | null
  used_at: string | null
  created_at: string
}

/**
 * UserAdmin - Admin user view
 */
export interface UserAdmin {
  id: number
  name: string
  role: 'user' | 'admin'
  is_active: boolean
  created_at: string
}
