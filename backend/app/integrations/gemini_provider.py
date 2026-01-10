"""
Google Gemini Vision API provider for receipt OCR.

This module implements the OCR provider interface using Google's Gemini Vision API.
"""

import logging
from typing import Dict, Any
import google.generativeai as genai

from .ocr_provider import BaseOCRProvider, OCRProvider, OCRProviderError
from .ocr_utils import (
    parse_json_response,
    validate_and_normalize_receipt_data,
    load_image_for_ocr,
)

logger = logging.getLogger(__name__)


class GeminiOCRProvider(BaseOCRProvider):
    """Google Gemini Vision API provider for receipt OCR."""

    def __init__(self, api_key: str):
        """
        Initialize Gemini OCR provider.

        Args:
            api_key: Google Gemini API key

        Raises:
            ValueError: If API key is invalid
        """
        super().__init__(api_key)

        # Validate and configure Gemini
        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"Invalid Gemini API key: {str(e)}")

    @property
    def provider_name(self) -> str:
        """Get the human-readable name of this provider."""
        return "Google Gemini"

    @property
    def provider_type(self) -> OCRProvider:
        """Get the provider type enum."""
        return OCRProvider.GEMINI

    async def scan_receipt(self, image_path: str) -> Dict[str, Any]:
        """
        Scan receipt image using Google Gemini Vision API.

        Args:
            image_path: Absolute path to the receipt image file

        Returns:
            Dictionary containing parsed receipt data

        Raises:
            OCRProviderError: If OCR processing fails
            FileNotFoundError: If image file doesn't exist
        """
        # Load image
        img = load_image_for_ocr(image_path)

        # Get standard OCR prompt
        from .ocr_provider import get_ocr_prompt
        prompt = get_ocr_prompt()

        try:
            model = genai.GenerativeModel('gemini-2.5-flash')

            logger.info(f"Processing receipt with Gemini: {image_path}")

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
                raise OCRProviderError("Empty response from Gemini API")

            response_text = response.text.strip()

            # Security: Log only metadata
            truncated_response = response_text[:100] + "..." if len(response_text) > 100 else response_text
            logger.debug(f"Gemini response received (length: {len(response_text)} chars): {truncated_response}")

            # Parse JSON response
            receipt_data = parse_json_response(response_text)

            # Validate and normalize data
            validated_data = validate_and_normalize_receipt_data(receipt_data)

            # Security: Log only metadata
            logger.info(
                f"Successfully extracted receipt data: "
                f"merchant={validated_data.get('merchant')}, "
                f"total={validated_data.get('total')} PLN, "
                f"items_count={len(validated_data.get('items', []))}"
            )

            return validated_data

        except genai.types.generation_types.BlockedPromptException as e:
            raise OCRProviderError(f"Gemini blocked the request: {str(e)}")
        except Exception as e:
            if isinstance(e, (OCRProviderError, FileNotFoundError, ValueError)):
                raise
            logger.error(f"Unexpected error during Gemini OCR: {str(e)}")
            raise OCRProviderError(f"Gemini OCR processing failed: {str(e)}")
