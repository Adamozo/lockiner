"""
OCR Provider abstraction layer.

This module provides a unified interface for different OCR providers
(Gemini, Claude, OpenAI) to process receipt images.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum


class OCRProvider(str, Enum):
    """Supported OCR providers."""
    GEMINI = "gemini"
    CLAUDE = "claude"
    OPENAI = "openai"


class OCRProviderError(Exception):
    """Base exception for OCR provider errors."""
    pass


class BaseOCRProvider(ABC):
    """
    Abstract base class for OCR providers.

    All OCR providers must implement this interface to ensure
    consistent behavior across different AI services.
    """

    def __init__(self, api_key: str):
        """
        Initialize OCR provider with API key.

        Args:
            api_key: API key for the provider

        Raises:
            ValueError: If API key is empty or invalid
        """
        if not api_key or not api_key.strip():
            raise ValueError(f"{self.__class__.__name__} API key is required")
        self.api_key = api_key.strip()

    @abstractmethod
    async def scan_receipt(self, image_path: str) -> Dict[str, Any]:
        """
        Scan receipt image and extract structured data.

        Args:
            image_path: Absolute path to the receipt image file

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
            OCRProviderError: If OCR processing fails
            FileNotFoundError: If image file doesn't exist
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the human-readable name of this provider."""
        pass

    @property
    @abstractmethod
    def provider_type(self) -> OCRProvider:
        """Get the provider type enum."""
        pass


def get_ocr_prompt() -> str:
    """
    Get the standard OCR prompt used across all providers.

    Returns:
        Standardized prompt for receipt extraction
    """
    return """Analyze this receipt image and extract all information as a JSON object.

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


def create_ocr_provider(provider_type: OCRProvider, api_key: str) -> BaseOCRProvider:
    """
    Factory function to create OCR provider instance.

    Args:
        provider_type: Type of OCR provider to create
        api_key: API key for the provider

    Returns:
        Instantiated OCR provider

    Raises:
        ValueError: If provider type is invalid or API key is invalid
        ImportError: If required package is not installed
    """
    from .gemini_provider import GeminiOCRProvider
    from .claude_provider import ClaudeOCRProvider
    from .openai_provider import OpenAIOCRProvider

    provider_map = {
        OCRProvider.GEMINI: GeminiOCRProvider,
        OCRProvider.CLAUDE: ClaudeOCRProvider,
        OCRProvider.OPENAI: OpenAIOCRProvider,
    }

    provider_class = provider_map.get(provider_type)
    if not provider_class:
        raise ValueError(f"Unknown OCR provider: {provider_type}")

    return provider_class(api_key)
