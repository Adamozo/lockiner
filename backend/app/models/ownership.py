"""Ownership Junction Tables for multi-tenant data access."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class UserTransaction(Base):
    __tablename__ = "user_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")
    transaction = relationship("Transaction")

    def __repr__(self):
        return f"<UserTransaction(user_id={self.user_id}, transaction_id={self.transaction_id})>"


class HouseholdTransaction(Base):
    __tablename__ = "household_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    added_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household")
    transaction = relationship("Transaction")
    added_by = relationship("User")

    def __repr__(self):
        return f"<HouseholdTransaction(household_id={self.household_id}, transaction_id={self.transaction_id})>"


class UserReceipt(Base):
    __tablename__ = "user_receipts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")
    receipt = relationship("Receipt")

    def __repr__(self):
        return f"<UserReceipt(user_id={self.user_id}, receipt_id={self.receipt_id})>"


class HouseholdReceipt(Base):
    __tablename__ = "household_receipts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False)
    added_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household")
    receipt = relationship("Receipt")
    added_by = relationship("User")

    def __repr__(self):
        return f"<HouseholdReceipt(household_id={self.household_id}, receipt_id={self.receipt_id})>"


class UserCategory(Base):
    __tablename__ = "user_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")
    category = relationship("Category")

    def __repr__(self):
        return f"<UserCategory(user_id={self.user_id}, category_id={self.category_id})>"


class HouseholdCategory(Base):
    __tablename__ = "household_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household")
    category = relationship("Category")

    def __repr__(self):
        return f"<HouseholdCategory(household_id={self.household_id}, category_id={self.category_id})>"


class UserBudgetSettings(Base):
    __tablename__ = "user_budget_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    budget_settings_id = Column(Integer, ForeignKey("budget_settings.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    user = relationship("User")
    budget_settings = relationship("BudgetSettings")

    def __repr__(self):
        return f"<UserBudgetSettings(user_id={self.user_id}, budget_settings_id={self.budget_settings_id})>"


class HouseholdBudgetSettings(Base):
    __tablename__ = "household_budget_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False)
    budget_settings_id = Column(Integer, ForeignKey("budget_settings.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    household = relationship("Household")
    budget_settings = relationship("BudgetSettings")

    def __repr__(self):
        return f"<HouseholdBudgetSettings(household_id={self.household_id}, budget_settings_id={self.budget_settings_id})>"
