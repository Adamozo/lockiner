"""Shopping Lists Module Models."""

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class ShoppingList(Base):
    """A shopping list with optional household sharing."""

    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="SET NULL"), nullable=True)
    visibility = Column(String, nullable=False, default="private")  # private | household
    name = Column(String, nullable=False)
    store_name = Column(String, nullable=True)
    planned_date = Column(String, nullable=True)  # ISO date YYYY-MM-DD
    status = Column(String, nullable=False, default="active")  # active | completed | archived
    notes = Column(Text, nullable=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    household = relationship("Household", foreign_keys=[household_id])
    items = relationship(
        "ShoppingListItem",
        back_populates="shopping_list",
        cascade="all, delete-orphan",
        order_by="ShoppingListItem.position",
    )

    def __repr__(self):
        return f"<ShoppingList(id={self.id}, name={self.name}, visibility={self.visibility})>"


class ShoppingListItem(Base):
    """A single item on a shopping list."""

    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    list_id = Column(Integer, ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False)
    added_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_product_id = Column(Integer, ForeignKey("food_products.id", ondelete="SET NULL"), nullable=True)
    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    category = Column(String, nullable=True)  # free text label
    status = Column(String, nullable=False, default="pending")  # pending | in_cart | purchased
    is_recurring = Column(Boolean, nullable=False, default=False)
    notes = Column(String, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(String, default=lambda: utc_now().isoformat())
    updated_at = Column(String, nullable=True)

    # Relationships
    shopping_list = relationship("ShoppingList", back_populates="items")

    def __repr__(self):
        return f"<ShoppingListItem(id={self.id}, name={self.name}, status={self.status})>"
