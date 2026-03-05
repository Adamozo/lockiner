"""Receipt schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ReceiptItem(BaseModel):
    """Individual item from receipt OCR."""
    name: str
    price: float
    quantity: Optional[int] = 1


class ReceiptBase(BaseModel):
    """Base schema for receipt data."""
    image_path: str
    scan_date: str = Field(..., description="Date in ISO 8601 format")
    merchant: Optional[str] = None
    total: Optional[float] = None
    payment_method: Optional[str] = None
    items_json: Optional[str] = Field(None, description="JSON array of items")
    raw_ocr_response: Optional[str] = None
    verified: bool = False
    category: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    """Schema for creating a new receipt."""
    pass


class ReceiptUpdate(BaseModel):
    """Schema for updating a receipt."""
    merchant: Optional[str] = None
    total: Optional[float] = None
    payment_method: Optional[str] = None
    items_json: Optional[str] = None
    verified: Optional[bool] = None
    category: Optional[str] = None


class ReceiptResponse(ReceiptBase):
    """Schema for receipt response."""
    id: int
    created_at: str
    additional_images: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class ReceiptItemDetailed(BaseModel):
    """Detailed receipt item with quantity and prices."""
    name: str
    quantity: int = 1
    unit_price: float
    total_price: float
    category: Optional[str] = None  # Item-level category (defaults to receipt category if not set)


class ReceiptOCRResponse(BaseModel):
    """Schema for OCR processing response."""
    merchant: str
    date: str
    total: float
    items: List[ReceiptItemDetailed]
    payment_method: Optional[str] = None
    tax_amount: Optional[float] = 0.0
    currency: str = "PLN"


class ReceiptUploadResponse(BaseModel):
    """Schema for receipt upload with OCR response."""
    receipt_id: int
    image_path: str
    ocr_data: Optional[ReceiptOCRResponse] = None
    error: Optional[str] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)
