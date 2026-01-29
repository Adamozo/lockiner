from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(String, nullable=False, index=True)  # ISO 8601: YYYY-MM-DD
    amount = Column(Float, nullable=False)
    description = Column(Text)
    category = Column(String, default="Inne", index=True)
    payment_method = Column(String, nullable=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    receipt = relationship("Receipt", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, date={self.date}, amount={self.amount}, category={self.category})>"
