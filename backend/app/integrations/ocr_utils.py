"""
Shared utilities for OCR providers.

This module contains common functions used by all OCR providers
for data validation, normalization, and processing.
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class OCRValidationError(Exception):
    """Exception raised when OCR data validation fails."""
    pass


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """
    Parse JSON response from OCR provider.

    Handles markdown code blocks and other formatting issues.

    Args:
        response_text: Raw text response from OCR provider

    Returns:
        Parsed JSON data

    Raises:
        OCRValidationError: If JSON parsing fails
    """
    response_text = response_text.strip()

    # Clean up response (remove markdown code blocks if present)
    if response_text.startswith("```json"):
        response_text = response_text[7:]  # Remove ```json
    if response_text.startswith("```"):
        response_text = response_text[3:]  # Remove ```
    if response_text.endswith("```"):
        response_text = response_text[:-3]  # Remove trailing ```

    response_text = response_text.strip()

    # Parse JSON response
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {response_text}")
        raise OCRValidationError(f"Invalid JSON response: {str(e)}")


def validate_and_normalize_receipt_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize receipt data to match expected schema.

    Args:
        data: Raw data from OCR provider

    Returns:
        Validated and normalized receipt data

    Raises:
        OCRValidationError: If data validation fails
    """
    try:
        # Normalize merchant
        merchant = str(data.get("merchant", "")).strip() or "Unknown Store"

        # Normalize date (ensure YYYY-MM-DD format)
        date_str = data.get("date", "")
        normalized_date = normalize_date(date_str)

        # Normalize total (ensure float)
        total = float(data.get("total", 0.0))

        # Normalize payment method
        payment_method = data.get("payment_method")
        valid_payment_methods = {"karta", "gotówka", "blik"}
        if payment_method and str(payment_method).lower() in valid_payment_methods:
            payment_method = str(payment_method).lower()
        else:
            payment_method = None

        # Normalize items
        items = data.get("items", [])
        normalized_items = []

        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    normalized_items.append({
                        "name": str(item.get("name", "Unknown item")).strip(),
                        "quantity": int(item.get("quantity", 1)),
                        "unit_price": float(item.get("unit_price", 0.0)),
                        "total_price": float(item.get("total_price", 0.0)),
                    })

        # Normalize tax amount
        tax_amount = float(data.get("tax_amount", 0.0))

        # Normalize currency
        currency = str(data.get("currency", "PLN")).upper()

        return {
            "merchant": merchant,
            "date": normalized_date,
            "total": total,
            "payment_method": payment_method,
            "items": normalized_items,
            "tax_amount": tax_amount,
            "currency": currency,
        }

    except (ValueError, TypeError, KeyError) as e:
        raise OCRValidationError(f"Data validation failed: {str(e)}")


def normalize_date(date_str: str) -> str:
    """
    Normalize date string to YYYY-MM-DD format.

    Handles common Polish receipt date formats:
    - DD.MM.YYYY
    - DD-MM-YYYY
    - DD/MM/YYYY
    - YYYY-MM-DD (already normalized)

    Args:
        date_str: Date string from receipt

    Returns:
        Normalized date in YYYY-MM-DD format

    Raises:
        OCRValidationError: If date parsing fails (returns today's date as fallback)
    """
    if not date_str:
        # Use today's date as fallback
        return datetime.now().date().isoformat()

    date_str = str(date_str).strip()

    # Try YYYY-MM-DD format (already normalized)
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        try:
            datetime.fromisoformat(date_str)
            return date_str
        except ValueError:
            pass

    # Try common Polish formats
    for fmt in ["%d.%m.%Y", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.date().isoformat()
        except ValueError:
            continue

    # If all formats fail, try to extract year-month-day
    import re
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    # Fallback to today's date
    logger.warning(f"Could not parse date '{date_str}', using today's date")
    return datetime.now().date().isoformat()


def load_image_for_ocr(image_path: str):
    """
    Load and prepare image for OCR processing.

    Args:
        image_path: Path to image file

    Returns:
        PIL Image object (RGB mode)

    Raises:
        FileNotFoundError: If image doesn't exist
        OCRValidationError: If image cannot be loaded
    """
    from pathlib import Path
    from PIL import Image

    image_file = Path(image_path)
    if not image_file.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    if not image_file.is_file():
        raise OCRValidationError(f"Path is not a file: {image_path}")

    try:
        img = Image.open(image_file)
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        return img
    except Exception as e:
        raise OCRValidationError(f"Failed to load image: {str(e)}")
