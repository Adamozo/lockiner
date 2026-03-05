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
    category = Column(String, ForeignKey("categories.name", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    # Relationships
    transactions = relationship("Transaction", back_populates="receipt")
    category_rel = relationship("Category", foreign_keys=[category])
    images = relationship(
        "ReceiptImage",
        back_populates="receipt",
        cascade="all, delete-orphan",
        order_by="ReceiptImage.sort_order",
        lazy="selectin",
    )

    @property
    def additional_images(self) -> list[str]:
        return [img.image_path for img in (self.images or [])]

    def __repr__(self):
        return f"<Receipt(id={self.id}, merchant={self.merchant}, total={self.total}, verified={self.verified})>"


class ReceiptImage(Base):
    __tablename__ = "receipt_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False, index=True)
    image_path = Column(String, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(String, default=lambda: utc_now().isoformat())

    receipt = relationship("Receipt", back_populates="images")

    def __repr__(self):
        return f"<ReceiptImage(id={self.id}, receipt_id={self.receipt_id}, sort_order={self.sort_order})>"
