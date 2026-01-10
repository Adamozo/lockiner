"""
Google Gemini Vision API integration for receipt OCR.

This module provides receipt scanning functionality using Google's Gemini Vision API.
It extracts structured data from receipt images with high accuracy for Polish receipts.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import google.generativeai as genai
from PIL import Image

logger = logging.getLogger(__name__)


class GeminiOCRError(Exception):
    """Custom exception for Gemini OCR processing errors."""
    pass


def scan_receipt(image_path: str, api_key: str) -> Dict[str, Any]:
    """
    Scan receipt image using Google Gemini Vision API.

    This function processes receipt images and extracts structured data including:
    - Merchant name
    - Receipt date
    - Total amount
    - Individual items with quantities and prices
    - Payment method
    - Tax information

    Args:
        image_path: Absolute path to the receipt image file
        api_key: Google Gemini API key

    Returns:
        Dictionary containing parsed receipt data matching the schema:
        {
            "merchant": str,
            "date": str (YYYY-MM-DD format),
            "total": float,
            "payment_method": str ("karta"|"gotówka"|"blik"|null),
            "items": [
                {
                    "name": str,
                    "quantity": int,
                    "unit_price": float,
                    "total_price": float
                }
            ],
            "tax_amount": float,
            "currency": str
        }

    Raises:
        GeminiOCRError: If API call fails, image is invalid, or JSON parsing fails
        FileNotFoundError: If image file doesn't exist
        ValueError: If API key is empty or invalid
    """
    # Validate inputs
    if not api_key or not api_key.strip():
        raise ValueError("Gemini API key is required")

    image_file = Path(image_path)
    if not image_file.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    if not image_file.is_file():
        raise ValueError(f"Path is not a file: {image_path}")

    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        raise ValueError(f"Invalid Gemini API key: {str(e)}")

    # Prepare the prompt for receipt extraction
    prompt = """Analyze this receipt image and extract all information as a JSON object.

IMPORTANT REQUIREMENTS:
1. Return ONLY valid JSON, no markdown, no explanations, no code blocks
2. Use YYYY-MM-DD format for dates (convert from DD.MM.YYYY or DD-MM-YYYY if needed)
3. All numbers must be valid floats (use dots, not commas)
4. Payment method must be one of: "karta", "gotówka", "blik", or null
5. If information is not visible, use null for strings and 0.0 for numbers
6. Extract ALL line items from the receipt

Expected JSON schema:
{
  "merchant": "Store name from receipt",
  "date": "YYYY-MM-DD",
  "total": 123.45,
  "payment_method": "karta",
  "items": [
    {
      "name": "Product name",
      "quantity": 1,
      "unit_price": 10.50,
      "total_price": 10.50
    }
  ],
  "tax_amount": 10.50,
  "currency": "PLN"
}

Extract data from this receipt:"""

    try:
        # Load and validate image
        try:
            img = Image.open(image_file)
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
        except Exception as e:
            raise GeminiOCRError(f"Failed to load image: {str(e)}")

        model = genai.GenerativeModel('gemini-2.5-flash')

        logger.info(f"Processing receipt image: {image_path}")

        # Generate content with vision
        response = model.generate_content(
            [prompt, img],
            generation_config=genai.GenerationConfig(
                temperature=0.1,  # Low temperature for consistent extraction
                max_output_tokens=2048,
            )
        )

        # Extract text response
        if not response or not response.text:
            raise GeminiOCRError("Empty response from Gemini API")

        response_text = response.text.strip()

        # Security: Log only metadata, not full response content
        # Truncate to 100 characters to prevent sensitive data in logs
        truncated_response = response_text[:100] + "..." if len(response_text) > 100 else response_text
        logger.debug(f"Gemini response received (length: {len(response_text)} chars): {truncated_response}")

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
            receipt_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {response_text}")
            raise GeminiOCRError(f"Invalid JSON response from Gemini: {str(e)}")

        # Validate required fields
        validated_data = _validate_and_normalize_receipt_data(receipt_data)

        # Security: Log only metadata, not full receipt data
        logger.info(
            f"Successfully extracted receipt data: "
            f"merchant={validated_data.get('merchant')}, "
            f"total={validated_data.get('total')} PLN, "
            f"items_count={len(validated_data.get('items', []))}"
        )
        return validated_data

    except genai.types.generation_types.BlockedPromptException as e:
        raise GeminiOCRError(f"Gemini blocked the request: {str(e)}")
    except Exception as e:
        if isinstance(e, (GeminiOCRError, FileNotFoundError, ValueError)):
            raise
        logger.error(f"Unexpected error during OCR: {str(e)}")
        raise GeminiOCRError(f"OCR processing failed: {str(e)}")


def _validate_and_normalize_receipt_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize receipt data to match expected schema.

    Args:
        data: Raw data from Gemini API

    Returns:
        Validated and normalized receipt data

    Raises:
        GeminiOCRError: If data validation fails
    """
    try:
        # Normalize merchant
        merchant = str(data.get("merchant", "")).strip() or "Unknown Store"

        # Normalize date (ensure YYYY-MM-DD format)
        date_str = data.get("date", "")
        normalized_date = _normalize_date(date_str)

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
        raise GeminiOCRError(f"Data validation failed: {str(e)}")


def _normalize_date(date_str: str) -> str:
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
        GeminiOCRError: If date parsing fails
    """
    from datetime import datetime

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


async def scan_receipt_async(image_path: str, api_key: str) -> Dict[str, Any]:
    """
    Async wrapper for scan_receipt.

    This is useful for FastAPI async endpoints, though the actual
    Gemini API call is synchronous.

    Args:
        image_path: Absolute path to the receipt image file
        api_key: Google Gemini API key

    Returns:
        Dictionary containing parsed receipt data

    Raises:
        GeminiOCRError: If OCR processing fails
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, scan_receipt, image_path, api_key)
