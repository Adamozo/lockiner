from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timezone
from collections import defaultdict

from ..models import BudgetSettings
from ..schemas import (
    CategorySpending,
    MonthSummary,
    SpendingTrend,
    YearlySummary,
    MerchantSpending,
    BudgetStatus,
    BudgetSettingsUpdate,
    OverallBudgetStatus,
    CompleteBudgetStatus,
    BudgetAlert,
    BudgetAlertsResponse,
    MemberSpending,
    HouseholdMonthlySummary,
    HouseholdCategorySummary,
    HouseholdSpendingByMember,
    HouseholdSpendingByCategory,
)
from ..repositories.analytics import AnalyticsRepository
from ..repositories.household import HouseholdRepository
from .ownership import OwnershipService

# ---------------------------------------


class InvalidMonthFormatError(Exception):
    def __init__(self):
        super().__init__("Invalid month format. Use YYYY-MM (e.g., '2024-01')")


class InvalidYearFormatError(Exception):
    def __init__(self):
        super().__init__("Invalid year format. Use YYYY (e.g., '2024')")


class InvalidTransactionTypeError(Exception):
    def __init__(self):
        super().__init__("Invalid type. Use 'expenses' or 'income'")


# ---------------------------------------


def format_currency(amount: float) -> str:
    """Format currency in PLN."""
    return f"{amount:,.2f} PLN"

# ---------------------------------------


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.repository: AnalyticsRepository = AnalyticsRepository(db)
        self.household_repository: HouseholdRepository = HouseholdRepository(db)
        self.ownership_service: OwnershipService = OwnershipService(db)
        self.db = db

    async def _resolve_household_id(self, household_uid: Optional[str]) -> Optional[int]:
        """Convert household UID (string) to household ID (int)."""
        if not household_uid:
            return None
        household = await self.household_repository.get_by_uid(household_uid)
        return household.id if household else None

    async def _get_accessible_transaction_ids(
        self,
        user_id: int,
        household_id: Optional[int] = None,
    ) -> list[int]:
        """Get list of transaction IDs that the user can access."""
        if household_id:
            return await self.ownership_service.get_household_entity_ids(
                "transaction", household_id
            )
        else:
            return await self.ownership_service.get_user_entity_ids(
                "transaction", user_id
            )

    async def _get_accessible_receipt_ids(
        self,
        user_id: int,
        household_id: Optional[int] = None,
    ) -> list[int]:
        """Get list of receipt IDs that the user can access."""
        if household_id:
            return await self.ownership_service.get_household_entity_ids(
                "receipt", household_id
            )
        else:
            return await self.ownership_service.get_user_entity_ids(
                "receipt", user_id
            )

    def _validate_month(self, month: str) -> None:
        try:
            datetime.strptime(month, "%Y-%m")

        except ValueError:
            raise InvalidMonthFormatError()

    def _validate_year(self, year: str) -> None:
        try:
            datetime.strptime(year, "%Y")

        except ValueError:
            raise InvalidYearFormatError()

    async def get_monthly_summary(
        self,
        month: str,
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> MonthSummary:
        self._validate_month(month)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Get accessible transaction IDs
        transaction_ids = None
        if user_id is not None:
            transaction_ids = await self._get_accessible_transaction_ids(user_id, household_id)

        transactions = await self.repository.get_transactions_by_month(month, transaction_ids)

        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
        net_amount = total_income - total_expenses
        transactions_count = len(transactions)

        category_stats = defaultdict(lambda: {"total": 0.0, "count": 0, "amounts": []})

        for t in transactions:
            if t.amount < 0:
                category_stats[t.category]["total"] += abs(t.amount)
                category_stats[t.category]["count"] += 1
                category_stats[t.category]["amounts"].append(abs(t.amount))

        by_category = []
        for cat_name, stats in category_stats.items():
            average = stats["total"] / stats["count"] if stats["count"] > 0 else 0.0
            percentage = (stats["total"] / total_expenses * 100) if total_expenses > 0 else 0.0

            by_category.append(
                CategorySpending(
                    category=cat_name,
                    total=stats["total"],
                    count=stats["count"],
                    average=average,
                    percentage=percentage,
                )
            )

        by_category.sort(key=lambda x: x.total, reverse=True)

        return MonthSummary(
            month=month,
            total_income=total_income,
            total_expenses=total_expenses,
            net_amount=net_amount,
            transactions_count=transactions_count,
            by_category=by_category,
        )

    async def get_spending_by_category(
        self,
        month: Optional[str] = None,
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> list[CategorySpending]:
        if month:
            self._validate_month(month)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Get accessible transaction IDs
        transaction_ids = None
        if user_id is not None:
            transaction_ids = await self._get_accessible_transaction_ids(user_id, household_id)

        transactions = await self.repository.get_expenses_by_month(month, transaction_ids)

        total_expenses = abs(sum(t.amount for t in transactions))

        category_stats = defaultdict(lambda: {"total": 0.0, "count": 0})

        for t in transactions:
            category_stats[t.category]["total"] += abs(t.amount)
            category_stats[t.category]["count"] += 1

        result = []
        for cat_name, stats in category_stats.items():
            average = stats["total"] / stats["count"] if stats["count"] > 0 else 0.0
            percentage = (stats["total"] / total_expenses * 100) if total_expenses > 0 else 0.0

            result.append(
                CategorySpending(
                    category=cat_name,
                    total=stats["total"],
                    count=stats["count"],
                    average=average,
                    percentage=percentage,
                )
            )

        result.sort(key=lambda x: x.total, reverse=True)

        return result

    async def get_top_transactions(
        self,
        limit: int = 10,
        month: Optional[str] = None,
        category: Optional[str] = None,
        transaction_type: str = "expenses",
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> list[dict]:
        if month:
            self._validate_month(month)

        if transaction_type not in ("expenses", "income"):
            raise InvalidTransactionTypeError()

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Get accessible transaction IDs
        transaction_ids = None
        if user_id is not None:
            transaction_ids = await self._get_accessible_transaction_ids(user_id, household_id)

        transactions = await self.repository.get_top_transactions(
            limit=limit,
            month=month,
            category=category,
            transaction_type=transaction_type,
            transaction_ids=transaction_ids,
        )

        result = []
        for t in transactions:
            result.append({
                "id": t.id,
                "date": t.date,
                "amount": t.amount,
                "description": t.description,
                "category": t.category,
                "notes": t.notes,
            })

        return result

    async def get_spending_trends(
        self,
        months: int = 6,
        category: Optional[str] = None,
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> list[SpendingTrend]:
        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Get accessible transaction IDs
        transaction_ids = None
        if user_id is not None:
            transaction_ids = await self._get_accessible_transaction_ids(user_id, household_id)

        transactions = await self.repository.get_expenses(category=category, transaction_ids=transaction_ids)

        monthly_totals = defaultdict(float)

        for t in transactions:
            month = t.date[:7] if len(t.date) >= 7 else t.date
            monthly_totals[month] += abs(t.amount)

        result = []
        for month, amount in monthly_totals.items():
            result.append(
                SpendingTrend(
                    month=month,
                    amount=amount,
                )
            )

        result.sort(key=lambda x: x.month)
        result = result[-months:]

        return result

    async def get_budget_status(
        self,
        month: str,
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> list[dict]:
        self._validate_month(month)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Get accessible transaction IDs
        transaction_ids = None
        if user_id is not None:
            transaction_ids = await self._get_accessible_transaction_ids(user_id, household_id)

        categories = await self.repository.get_categories_with_budget()

        result = []
        for category in categories:
            transactions = await self.repository.get_category_transactions(
                category.name, month, transaction_ids
            )

            spent = abs(sum(t.amount for t in transactions))
            budget = category.budget_limit or 0.0
            remaining = budget - spent
            percentage = (spent / budget * 100) if budget > 0 else 0.0

            result.append({
                "category": category.name,
                "icon": category.icon,
                "color": category.color,
                "budget_limit": budget,
                "spent": spent,
                "remaining": remaining,
                "percentage": percentage,
                "status": "over" if spent > budget else "warning" if percentage > 80 else "ok",
            })

        result.sort(key=lambda x: x["percentage"], reverse=True)

        return result

    async def get_yearly_summary(
        self,
        year: str,
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> YearlySummary:
        self._validate_year(year)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Get accessible IDs
        transaction_ids = None
        receipt_ids = None
        if user_id is not None:
            transaction_ids = await self._get_accessible_transaction_ids(user_id, household_id)
            receipt_ids = await self._get_accessible_receipt_ids(user_id, household_id)

        transactions = await self.repository.get_transactions_by_year(year, transaction_ids)
        receipts = await self.repository.get_receipts_by_year(year, receipt_ids)

        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
        net_amount = total_income - total_expenses
        transactions_count = len(transactions)
        receipts_count = len(receipts)

        category_stats = defaultdict(lambda: {"total": 0.0, "count": 0, "amounts": []})

        for t in transactions:
            if t.amount < 0:
                category_stats[t.category]["total"] += abs(t.amount)
                category_stats[t.category]["count"] += 1
                category_stats[t.category]["amounts"].append(abs(t.amount))

        by_category = []
        for cat_name, stats in category_stats.items():
            average = stats["total"] / stats["count"] if stats["count"] > 0 else 0.0
            percentage = (stats["total"] / total_expenses * 100) if total_expenses > 0 else 0.0

            by_category.append(
                CategorySpending(
                    category=cat_name,
                    total=stats["total"],
                    count=stats["count"],
                    average=average,
                    percentage=percentage,
                )
            )

        by_category.sort(key=lambda x: x.total, reverse=True)

        monthly_data = defaultdict(lambda: {
            "income": 0.0,
            "expenses": 0.0,
            "count": 0,
            "categories": defaultdict(lambda: {"total": 0.0, "count": 0})
        })

        for t in transactions:
            month = t.date[:7] if len(t.date) >= 7 else t.date
            if t.amount > 0:
                monthly_data[month]["income"] += t.amount
            else:
                monthly_data[month]["expenses"] += abs(t.amount)
                monthly_data[month]["categories"][t.category]["total"] += abs(t.amount)
                monthly_data[month]["categories"][t.category]["count"] += 1
            monthly_data[month]["count"] += 1

        monthly_breakdown = []
        for month, data in sorted(monthly_data.items()):
            month_categories = []
            for cat_name, cat_stats in data["categories"].items():
                average = cat_stats["total"] / cat_stats["count"] if cat_stats["count"] > 0 else 0.0
                percentage = (cat_stats["total"] / data["expenses"] * 100) if data["expenses"] > 0 else 0.0
                month_categories.append(
                    CategorySpending(
                        category=cat_name,
                        total=cat_stats["total"],
                        count=cat_stats["count"],
                        average=average,
                        percentage=percentage,
                    )
                )

            month_categories.sort(key=lambda x: x.total, reverse=True)

            monthly_breakdown.append(
                MonthSummary(
                    month=month,
                    total_income=data["income"],
                    total_expenses=data["expenses"],
                    net_amount=data["income"] - data["expenses"],
                    transactions_count=data["count"],
                    by_category=month_categories,
                )
            )

        return YearlySummary(
            year=year,
            total_income=total_income,
            total_expenses=total_expenses,
            net_amount=net_amount,
            transactions_count=transactions_count,
            receipts_count=receipts_count,
            by_category=by_category,
            monthly_breakdown=monthly_breakdown,
        )

    async def get_spending_by_merchant(
        self,
        month: Optional[str] = None,
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> list[MerchantSpending]:
        if month:
            self._validate_month(month)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        # Get accessible receipt IDs
        receipt_ids = None
        if user_id is not None:
            receipt_ids = await self._get_accessible_receipt_ids(user_id, household_id)

        receipts = await self.repository.get_receipts_by_month(month, receipt_ids)

        total_spending = sum(r.total for r in receipts)

        merchant_stats = defaultdict(lambda: {"total": 0.0, "count": 0})

        for r in receipts:
            merchant_stats[r.merchant]["total"] += r.total
            merchant_stats[r.merchant]["count"] += 1

        result = []
        for merchant_name, stats in merchant_stats.items():
            average = stats["total"] / stats["count"] if stats["count"] > 0 else 0.0
            percentage = (stats["total"] / total_spending * 100) if total_spending > 0 else 0.0

            result.append(
                MerchantSpending(
                    merchant=merchant_name,
                    total=stats["total"],
                    receipts_count=stats["count"],
                    average=average,
                    percentage=percentage,
                )
            )

        result.sort(key=lambda x: x.total, reverse=True)

        return result

    async def get_budget_settings(
        self,
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> BudgetSettings:
        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)
        settings = None

        # Try household settings first if household_id provided
        if household_id:
            settings = await self.repository.get_household_budget_settings(household_id)

        # Then try user settings
        if settings is None and user_id:
            settings = await self.repository.get_user_budget_settings(user_id)

        # Create default settings for user if none exist
        if settings is None:
            settings = BudgetSettings()
            settings = await self.repository.create_budget_settings(settings)

            # Create ownership record
            if user_id:
                if household_id:
                    await self.ownership_service.assign_to_household(
                        "budget_settings", settings.id, household_id
                    )
                else:
                    await self.ownership_service.assign_to_user(
                        "budget_settings", settings.id, user_id
                    )

        return settings

    async def update_budget_settings(
        self,
        data: BudgetSettingsUpdate,
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> BudgetSettings:
        settings = await self.get_budget_settings(user_id, household_uid)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        settings.updated_at = datetime.now(timezone.utc).isoformat()

        try:
            return await self.repository.update_budget_settings(settings)

        except Exception as e:
            await self.db.rollback()
            raise

    async def get_complete_budget_status(
        self,
        month: str,
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> CompleteBudgetStatus:
        self._validate_month(month)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        settings = await self.get_budget_settings(user_id, household_uid)

        # Get accessible transaction IDs
        transaction_ids = None
        if user_id is not None:
            transaction_ids = await self._get_accessible_transaction_ids(user_id, household_id)

        transactions = await self.repository.get_expenses_by_month(month, transaction_ids)
        total_spent = abs(sum(t.amount for t in transactions))

        overall_limit = settings.overall_monthly_limit

        if overall_limit:
            remaining = overall_limit - total_spent
            percentage = (total_spent / overall_limit * 100) if overall_limit > 0 else 0.0

            if percentage >= settings.alert_threshold_danger:
                status_str = "over"
                alert_message = f"You've exceeded your monthly budget by {format_currency(abs(remaining))}"
            elif percentage >= settings.alert_threshold_warning:
                status_str = "warning"
                alert_message = f"You're approaching your monthly budget limit. {format_currency(remaining)} remaining."
            else:
                status_str = "ok"
                alert_message = None
        else:
            remaining = 0
            percentage = 0
            status_str = "no_limit"
            alert_message = None

        overall_status = OverallBudgetStatus(
            month=month,
            overall_limit=overall_limit,
            total_spent=total_spent,
            remaining=remaining,
            percentage=percentage,
            status=status_str,
            alert_message=alert_message,
        )

        categories = await self.repository.get_categories_with_budget()

        category_statuses = []
        for category in categories:
            cat_transactions = await self.repository.get_category_transactions(
                category.name, month, transaction_ids
            )

            spent = abs(sum(t.amount for t in cat_transactions))
            budget = category.budget_limit or 0.0
            remaining = budget - spent
            percentage = (spent / budget * 100) if budget > 0 else 0.0

            category_statuses.append(
                BudgetStatus(
                    category=category.name,
                    icon=category.icon,
                    color=category.color,
                    budget_limit=budget,
                    spent=spent,
                    remaining=remaining,
                    percentage=percentage,
                    status="over" if spent > budget else "warning" if percentage > 80 else "ok",
                )
            )

        category_statuses.sort(key=lambda x: x.percentage, reverse=True)

        return CompleteBudgetStatus(
            overall=overall_status,
            categories=category_statuses,
            settings=settings,
        )

    async def check_budget_alerts(
        self,
        month: str,
        user_id: Optional[int] = None,
        household_uid: Optional[str] = None,
    ) -> BudgetAlertsResponse:
        settings = await self.get_budget_settings(user_id, household_uid)
        if settings is None or not settings.enable_alerts:
            return BudgetAlertsResponse(alerts=[])

        alerts = []

        complete_status = await self.get_complete_budget_status(month, user_id, household_uid)

        overall = complete_status.overall
        if overall.status in ["warning", "over"] and overall.alert_message:
            alerts.append(
                BudgetAlert(
                    type="overall",
                    severity=overall.status,
                    message=overall.alert_message,
                    category=None,
                )
            )

        for cat in complete_status.categories:
            if cat.status == "over":
                alerts.append(
                    BudgetAlert(
                        type="category",
                        severity="over",
                        message=f"{cat.category}: Over budget by {format_currency(abs(cat.remaining))}",
                        category=cat.category,
                        icon=cat.icon,
                        color=cat.color,
                    )
                )
            elif cat.status == "warning":
                alerts.append(
                    BudgetAlert(
                        type="category",
                        severity="warning",
                        message=f"{cat.category}: {cat.percentage:.0f}% of budget used",
                        category=cat.category,
                        icon=cat.icon,
                        color=cat.color,
                    )
                )

        return BudgetAlertsResponse(alerts=alerts)

    # ============================================================================
    # Household Analytics Methods
    # ============================================================================

    async def get_household_monthly_summary(
        self,
        household_id: int,
        month: str,
    ) -> HouseholdMonthlySummary:
        """Get monthly summary for a household with breakdown by member."""
        self._validate_month(month)

        transactions_with_users = await self.repository.get_household_transactions(
            household_id, month
        )

        total_income = 0.0
        total_expenses = 0.0
        transactions_count = len(transactions_with_users)

        category_stats = defaultdict(lambda: {"total": 0.0, "count": 0})
        member_stats = defaultdict(lambda: {"total": 0.0, "count": 0, "name": "Unknown"})

        for transaction, user in transactions_with_users:
            if transaction.amount > 0:
                total_income += transaction.amount
            else:
                expense_amount = abs(transaction.amount)
                total_expenses += expense_amount

                # Category breakdown
                category_stats[transaction.category]["total"] += expense_amount
                category_stats[transaction.category]["count"] += 1

                # Member breakdown
                if user:
                    member_stats[user.id]["total"] += expense_amount
                    member_stats[user.id]["count"] += 1
                    member_stats[user.id]["name"] = user.name

        net_amount = total_income - total_expenses

        # Build category spending list
        by_category = []
        for cat_name, stats in category_stats.items():
            average = stats["total"] / stats["count"] if stats["count"] > 0 else 0.0
            percentage = (stats["total"] / total_expenses * 100) if total_expenses > 0 else 0.0

            by_category.append(
                CategorySpending(
                    category=cat_name,
                    total=stats["total"],
                    count=stats["count"],
                    average=average,
                    percentage=percentage,
                )
            )

        by_category.sort(key=lambda x: x.total, reverse=True)

        # Build member spending list
        by_member = []
        for user_id, stats in member_stats.items():
            average = stats["total"] / stats["count"] if stats["count"] > 0 else 0.0
            percentage = (stats["total"] / total_expenses * 100) if total_expenses > 0 else 0.0

            by_member.append(
                MemberSpending(
                    user_id=user_id,
                    user_name=stats["name"],
                    total=stats["total"],
                    count=stats["count"],
                    average=average,
                    percentage=percentage,
                )
            )

        by_member.sort(key=lambda x: x.total, reverse=True)

        return HouseholdMonthlySummary(
            month=month,
            total_income=total_income,
            total_expenses=total_expenses,
            net_amount=net_amount,
            transactions_count=transactions_count,
            by_category=by_category,
            by_member=by_member,
        )

    async def get_household_spending_by_member(
        self,
        household_id: int,
        month: Optional[str] = None,
    ) -> HouseholdSpendingByMember:
        """Get spending breakdown by household member."""
        if month:
            self._validate_month(month)

        expenses_with_users = await self.repository.get_household_expenses(
            household_id, month
        )

        total_expenses = sum(abs(t.amount) for t, _ in expenses_with_users)

        member_stats = defaultdict(lambda: {"total": 0.0, "count": 0, "name": "Unknown"})

        for transaction, user in expenses_with_users:
            if user:
                expense_amount = abs(transaction.amount)
                member_stats[user.id]["total"] += expense_amount
                member_stats[user.id]["count"] += 1
                member_stats[user.id]["name"] = user.name

        members = []
        for user_id, stats in member_stats.items():
            average = stats["total"] / stats["count"] if stats["count"] > 0 else 0.0
            percentage = (stats["total"] / total_expenses * 100) if total_expenses > 0 else 0.0

            members.append(
                MemberSpending(
                    user_id=user_id,
                    user_name=stats["name"],
                    total=stats["total"],
                    count=stats["count"],
                    average=average,
                    percentage=percentage,
                )
            )

        members.sort(key=lambda x: x.total, reverse=True)

        return HouseholdSpendingByMember(
            month=month,
            members=members,
            total=total_expenses,
        )

    async def get_household_spending_by_category(
        self,
        household_id: int,
        month: Optional[str] = None,
    ) -> HouseholdSpendingByCategory:
        """Get spending breakdown by category with member contributions."""
        if month:
            self._validate_month(month)

        expenses_with_users = await self.repository.get_household_expenses(
            household_id, month
        )

        total_expenses = sum(abs(t.amount) for t, _ in expenses_with_users)

        # Nested structure: category -> member_id -> stats
        category_member_stats = defaultdict(
            lambda: defaultdict(lambda: {"total": 0.0, "count": 0, "name": "Unknown"})
        )
        category_totals = defaultdict(lambda: {"total": 0.0, "count": 0})

        for transaction, user in expenses_with_users:
            expense_amount = abs(transaction.amount)
            category = transaction.category

            # Category totals
            category_totals[category]["total"] += expense_amount
            category_totals[category]["count"] += 1

            # Member contribution to this category
            if user:
                category_member_stats[category][user.id]["total"] += expense_amount
                category_member_stats[category][user.id]["count"] += 1
                category_member_stats[category][user.id]["name"] = user.name

        categories = []
        for category, cat_stats in category_totals.items():
            cat_total = cat_stats["total"]
            cat_count = cat_stats["count"]
            cat_average = cat_total / cat_count if cat_count > 0 else 0.0
            cat_percentage = (cat_total / total_expenses * 100) if total_expenses > 0 else 0.0

            # Build member breakdown for this category
            member_list = []
            for user_id, member_data in category_member_stats[category].items():
                m_average = member_data["total"] / member_data["count"] if member_data["count"] > 0 else 0.0
                m_percentage = (member_data["total"] / cat_total * 100) if cat_total > 0 else 0.0

                member_list.append(
                    MemberSpending(
                        user_id=user_id,
                        user_name=member_data["name"],
                        total=member_data["total"],
                        count=member_data["count"],
                        average=m_average,
                        percentage=m_percentage,
                    )
                )

            member_list.sort(key=lambda x: x.total, reverse=True)

            categories.append(
                HouseholdCategorySummary(
                    category=category,
                    total=cat_total,
                    count=cat_count,
                    average=cat_average,
                    percentage=cat_percentage,
                    by_member=member_list,
                )
            )

        categories.sort(key=lambda x: x.total, reverse=True)

        return HouseholdSpendingByCategory(
            month=month,
            categories=categories,
            total=total_expenses,
        )
