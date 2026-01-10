"""
Integrations package for external 3rd party services.

This package contains integrations with:
- Google Gemini (OCR)
- OpenAI (OCR)
- Anthropic Claude (OCR)
"""

from .gemini_ocr import scan_receipt, scan_receipt_async, GeminiOCRError
from .ocr_provider import create_ocr_provider, OCRProvider, OCRProviderError

__all__ = [
    "scan_receipt",
    "scan_receipt_async",
    "GeminiOCRError",
    "create_ocr_provider",
    "OCRProvider",
    "OCRProviderError",
]
