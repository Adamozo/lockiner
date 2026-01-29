from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base, utc_now


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_path = Column(String, nullable=False)
    scan_date = Column(String, nullable=False, index=True)  # ISO 8601: YYYY-MM-DD
    merchant = Column(String, index=True)
    total = Column(Float)
    payment_method = Column(String, nullable=True)
    items_json = Column(Text)
    raw_ocr_response = Column(Text)
    verified = Column(Boolean, default=False)
    category = Column(String, ForeignKey("categories.name"), default="Inne", index=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    transactions = relationship("Transaction", back_populates="receipt")
    category_rel = relationship("Category", foreign_keys=[category])

    def __repr__(self):
        return f"<Receipt(id={self.id}, merchant={self.merchant}, total={self.total}, verified={self.verified})>"
