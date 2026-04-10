"""
Pydantic schemas for request/response validation.

This module defines Pydantic models for API request validation
and response serialization. Follows Pydantic V2 syntax.

All schemas are re-exported from submodules for backward compatibility.
"""

# Transaction schemas
from .transaction import (
    TransactionBase,
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
)

# Receipt schemas
from .receipt import (
    ReceiptItem,
    ReceiptBase,
    ReceiptCreate,
    ReceiptUpdate,
    ReceiptResponse,
    ReceiptItemDetailed,
    ReceiptOCRResponse,
    ReceiptUploadResponse,
)

# Category schemas
from .category import (
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)

# Monthly import schemas
from .monthly_import import (
    MonthlyImportBase,
    MonthlyImportCreate,
    MonthlyImportResponse,
)

# Analytics schemas
from .analytics import (
    CategorySpending,
    MonthSummary,
    SpendingTrend,
    YearlySummary,
    MerchantSpending,
    BudgetStatus,
)

# Budget schemas
from .budget import (
    BudgetSettingsBase,
    BudgetSettingsUpdate,
    BudgetSettingsResponse,
    OverallBudgetStatus,
    CompleteBudgetStatus,
    BudgetAlert,
    BudgetAlertsResponse,
)

# CSV import schemas
from .csv_import import (
    CSVImportRequest,
    CSVImportResponse,
)

# Error schemas
from .error import (
    ErrorResponse,
    ValidationErrorResponse,
)

# Settings schemas
from .settings import (
    APIProviderConfigBase,
    APIProviderConfigCreate,
    APIProviderConfigResponse,
    APIProviderListResponse,
    SetActiveProviderRequest,
)

# Voucher schemas
from .voucher import (
    VoucherResponse,
    VoucherValidateResponse,
)

# User schemas
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordChangeRequest,
    ResetPasswordWithDekRequest,
)

# Household schemas
from .household import (
    HouseholdBase,
    HouseholdCreate,
    HouseholdUpdate,
    HouseholdMemberResponse,
    HouseholdResponse,
    HouseholdDetailResponse,
    HouseholdMemberUpdate,
)

# Invitation schemas
from .invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationJoinResponse,
)

# Household analytics schemas
from .household_analytics import (
    MemberSpending,
    HouseholdMonthlySummary,
    HouseholdCategorySummary,
    HouseholdSpendingByMember,
    HouseholdSpendingByCategory,
)

# Food schemas
from .food import (
    FoodCategoryBase,
    FoodCategoryCreate,
    FoodCategoryResponse,
    FoodProductBase,
    FoodProductCreate,
    FoodProductUpdate,
    FoodProductResponse,
    FoodProductAliasCreate,
    FoodProductAliasResponse,
    FoodPendingImportItemResponse,
    FoodPendingImportResponse,
    FoodPendingImportItemAccept,
    FoodPendingImportItemBulkAccept,
    FoodInventoryCreate,
    FoodInventoryUpdate,
    FoodInventoryResponse,
    FoodInventoryConsumeRequest,
    FoodExpiryReminderResponse,
    FoodReminderSettingsBase,
    FoodReminderSettingsUpdate,
    FoodReminderSettingsResponse,
    FoodConsumptionLogCreate,
    FoodConsumptionLogResponse,
    FoodProductSearchParams,
    FoodInventoryFilterParams,
    InventoryItemForProduct,
    OFFProductInfo,
    ProductWithInventoryResponse,
    DirectConsumptionRequest,
    MacroSummary,
    MealLogEntry,
    MealSummary,
    GoalSummary,
    DailyNutritionSummary,
    WeeklyNutritionDay,
    FoodDailyGoalResponse,
    FoodDailyGoalUpdate,
)

# Fitness schemas
from .fitness import (
    ExerciseSetCreate,
    ExerciseSetResponse,
    ExerciseBase,
    ExerciseCreate,
    ExerciseResponse,
    WorkoutBase,
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutResponse,
    WeightEntryBase,
    WeightEntryCreate,
    WeightEntryUpdate,
    WeightEntryResponse,
    FitnessStatsResponse,
    UserBodyProfileResponse,
    UserBodyProfileUpdate,
    BodyMeasurementEntryCreate,
    BodyMeasurementEntryUpdate,
    BodyMeasurementEntryResponse,
    WorkoutTemplateExerciseCreate,
    WorkoutTemplateExerciseResponse,
    WorkoutTemplateCreate,
    WorkoutTemplateUpdate,
    WorkoutTemplateResponse,
)

# Notification schedule schemas
from .notification_schedule import (
    NotificationScheduleBase,
    NotificationScheduleUpdate,
    NotificationScheduleResponse,
    NotificationScheduleBulkUpdate,
    NotificationScheduleListResponse,
    CustomReminderCreate,
)

# Journal schemas
from .journal import (
    JournalItemCreate,
    JournalItemResponse,
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    JournalStatsResponse,
    ReportGenerateRequest,
    JournalReportResponse,
    ReportData,
    CategoryReportData,
    MeditationSessionCreate,
    MeditationSessionUpdate,
    MeditationSessionResponse,
    MeditationStatsResponse,
)

# Backup schemas
from .backup import (
    BackupScheduleUpdate,
    BackupPasswordSet,
    BackupSettingsResponse,
    HouseholdBackupSettingsResponse,
)

# Medicine schemas
from .medicine import (
    MedicineCreate,
    MedicineUpdate,
    MedicineResponse,
    MedicineScheduleCreate,
    MedicineScheduleUpdate,
    MedicineScheduleResponse,
    MedicineLogResponse,
    MedicineLogMarkTaken,
    TodayDoseResponse,
    MedicineStatsResponse,
)

# OAuth schemas
from .oauth import OAuthAuthorizeParams, OAuthTokenRequest, OAuthTokenResponse, OAuthUserInfoResponse

# Assistant schemas
from .assistant import AssistantMessage, AssistantChatRequest, AssistantChatResponse

# Food recipes schemas
from .food_recipes import (
    RecipeIngredientCreate,
    RecipeIngredientResponse,
    FoodRecipeCreate,
    FoodRecipeUpdate,
    FoodRecipeRating,
    FoodRecipeResponse,
    RecipeGenerateRequest,
    RecipeMatchIngredient,
    RecipeMatchResult,
)

# Two-factor authentication schemas
from .two_factor import (
    TwoFactorSetupResponse,
    TwoFactorVerifySetupRequest,
    TwoFactorVerifySetupResponse,
    TwoFactorDisableRequest,
    TwoFactorStatusResponse,
    TwoFactorVerifyLoginRequest,
    TwoFactorRegenerateRequest,
    TwoFactorRegenerateResponse,
    LoginResponse,
)

__all__ = [
    # Transaction
    "TransactionBase",
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    # Receipt
    "ReceiptItem",
    "ReceiptBase",
    "ReceiptCreate",
    "ReceiptUpdate",
    "ReceiptResponse",
    "ReceiptItemDetailed",
    "ReceiptOCRResponse",
    "ReceiptUploadResponse",
    # Category
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    # Monthly import
    "MonthlyImportBase",
    "MonthlyImportCreate",
    "MonthlyImportResponse",
    # Analytics
    "CategorySpending",
    "MonthSummary",
    "SpendingTrend",
    "YearlySummary",
    "MerchantSpending",
    "BudgetStatus",
    # Budget
    "BudgetSettingsBase",
    "BudgetSettingsUpdate",
    "BudgetSettingsResponse",
    "OverallBudgetStatus",
    "CompleteBudgetStatus",
    "BudgetAlert",
    "BudgetAlertsResponse",
    # CSV import
    "CSVImportRequest",
    "CSVImportResponse",
    # Error
    "ErrorResponse",
    "ValidationErrorResponse",
    # Settings
    "APIProviderConfigBase",
    "APIProviderConfigCreate",
    "APIProviderConfigResponse",
    "APIProviderListResponse",
    "SetActiveProviderRequest",
    # Voucher
    "VoucherResponse",
    "VoucherValidateResponse",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordChangeRequest",
    "ResetPasswordWithDekRequest",
    # Household
    "HouseholdBase",
    "HouseholdCreate",
    "HouseholdUpdate",
    "HouseholdMemberResponse",
    "HouseholdResponse",
    "HouseholdDetailResponse",
    "HouseholdMemberUpdate",
    # Invitation
    "InvitationCreate",
    "InvitationResponse",
    "InvitationJoinResponse",
    # Household analytics
    "MemberSpending",
    "HouseholdMonthlySummary",
    "HouseholdCategorySummary",
    "HouseholdSpendingByMember",
    "HouseholdSpendingByCategory",
    # Food
    "FoodCategoryBase",
    "FoodCategoryCreate",
    "FoodCategoryResponse",
    "FoodProductBase",
    "FoodProductCreate",
    "FoodProductUpdate",
    "FoodProductResponse",
    "FoodProductAliasCreate",
    "FoodProductAliasResponse",
    "FoodPendingImportItemResponse",
    "FoodPendingImportResponse",
    "FoodPendingImportItemAccept",
    "FoodPendingImportItemBulkAccept",
    "FoodInventoryCreate",
    "FoodInventoryUpdate",
    "FoodInventoryResponse",
    "FoodInventoryConsumeRequest",
    "FoodExpiryReminderResponse",
    "FoodReminderSettingsBase",
    "FoodReminderSettingsUpdate",
    "FoodReminderSettingsResponse",
    "FoodConsumptionLogCreate",
    "FoodConsumptionLogResponse",
    "FoodProductSearchParams",
    "FoodInventoryFilterParams",
    "InventoryItemForProduct",
    "OFFProductInfo",
    "ProductWithInventoryResponse",
    "DirectConsumptionRequest",
    "MacroSummary",
    "MealLogEntry",
    "MealSummary",
    "GoalSummary",
    "DailyNutritionSummary",
    "WeeklyNutritionDay",
    "FoodDailyGoalResponse",
    "FoodDailyGoalUpdate",
    # Fitness
    "ExerciseSetCreate",
    "ExerciseSetResponse",
    "ExerciseBase",
    "ExerciseCreate",
    "ExerciseResponse",
    "WorkoutBase",
    "WorkoutCreate",
    "WorkoutUpdate",
    "WorkoutResponse",
    "WeightEntryBase",
    "WeightEntryCreate",
    "WeightEntryUpdate",
    "WeightEntryResponse",
    "FitnessStatsResponse",
    "UserBodyProfileResponse",
    "UserBodyProfileUpdate",
    "BodyMeasurementEntryCreate",
    "BodyMeasurementEntryUpdate",
    "BodyMeasurementEntryResponse",
    "WorkoutTemplateExerciseCreate",
    "WorkoutTemplateExerciseResponse",
    "WorkoutTemplateCreate",
    "WorkoutTemplateUpdate",
    "WorkoutTemplateResponse",
    # Notification schedules
    "NotificationScheduleBase",
    "NotificationScheduleUpdate",
    "NotificationScheduleResponse",
    "NotificationScheduleBulkUpdate",
    "NotificationScheduleListResponse",
    "CustomReminderCreate",
    # Two-factor authentication
    "TwoFactorSetupResponse",
    "TwoFactorVerifySetupRequest",
    "TwoFactorVerifySetupResponse",
    "TwoFactorDisableRequest",
    "TwoFactorStatusResponse",
    "TwoFactorVerifyLoginRequest",
    "TwoFactorRegenerateRequest",
    "TwoFactorRegenerateResponse",
    "LoginResponse",
    # Medicine
    "MedicineCreate",
    "MedicineUpdate",
    "MedicineResponse",
    "MedicineScheduleCreate",
    "MedicineScheduleUpdate",
    "MedicineScheduleResponse",
    "MedicineLogResponse",
    "MedicineLogMarkTaken",
    "TodayDoseResponse",
    "MedicineStatsResponse",
    # Backup
    "BackupScheduleUpdate",
    "BackupPasswordSet",
    "BackupSettingsResponse",
    "HouseholdBackupSettingsResponse",
    # Journal
    "JournalItemCreate",
    "JournalItemResponse",
    "JournalEntryCreate",
    "JournalEntryUpdate",
    "JournalEntryResponse",
    "JournalStatsResponse",
    "ReportGenerateRequest",
    "JournalReportResponse",
    "ReportData",
    "CategoryReportData",
    "MeditationSessionCreate",
    "MeditationSessionUpdate",
    "MeditationSessionResponse",
    "MeditationStatsResponse",
]
