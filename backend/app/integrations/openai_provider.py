"""
OpenAI Vision API provider for receipt OCR.

This module implements the OCR provider interface using OpenAI's GPT-4 Vision API.
"""

import logging
import base64
from typing import Dict, Any
from pathlib import Path

from .ocr_provider import BaseOCRProvider, OCRProvider, OCRProviderError
from .ocr_utils import (
    parse_json_response,
    validate_and_normalize_receipt_data,
    load_image_for_ocr,
)

logger = logging.getLogger(__name__)


class OpenAIOCRProvider(BaseOCRProvider):
    """OpenAI GPT-4 Vision API provider for receipt OCR."""

    def __init__(self, api_key: str):
        """
        Initialize OpenAI OCR provider.

        Args:
            api_key: OpenAI API key

        Raises:
            ValueError: If API key is invalid
        """
        super().__init__(api_key)

        # Validate that openai package is installed
        try:
            import openai
            self.openai = openai
        except ImportError:
            raise ValueError(
                "OpenAI package not installed. "
                "Install with: pip install openai"
            )

    @property
    def provider_name(self) -> str:
        """Get the human-readable name of this provider."""
        return "OpenAI GPT-4 Vision"

    @property
    def provider_type(self) -> OCRProvider:
        """Get the provider type enum."""
        return OCRProvider.OPENAI

    def _encode_image(self, image_path: str) -> str:
        """
        Encode image as base64 for OpenAI API.

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded image string with data URI prefix
        """
        # Load image to validate it
        load_image_for_ocr(image_path)

        # Read file as bytes and encode
        with open(image_path, 'rb') as f:
            image_data = f.read()

        base64_data = base64.b64encode(image_data).decode('utf-8')

        # Determine media type
        suffix = Path(image_path).suffix.lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        media_type = media_type_map.get(suffix, 'image/jpeg')

        return f"data:{media_type};base64,{base64_data}"

    async def scan_receipt(self, image_path: str) -> Dict[str, Any]:
        """
        Scan receipt image using OpenAI GPT-4 Vision API.

        Args:
            image_path: Absolute path to the receipt image file

        Returns:
            Dictionary containing parsed receipt data

        Raises:
            OCRProviderError: If OCR processing fails
            FileNotFoundError: If image file doesn't exist
        """
        # Encode image
        try:
            base64_image = self._encode_image(image_path)
        except Exception as e:
            raise OCRProviderError(f"Failed to encode image: {str(e)}")

        # Get standard OCR prompt
        from .ocr_provider import get_ocr_prompt
        prompt = get_ocr_prompt()

        try:
            client = self.openai.OpenAI(api_key=self.api_key)

            logger.info(f"Processing receipt with OpenAI: {image_path}")

            # Call OpenAI API with vision
            response = client.chat.completions.create(
                model="gpt-4o",
                max_tokens=2048,
                temperature=0.1,  # Low temperature for consistent extraction
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": base64_image
                                }
                            }
                        ]
                    }
                ]
            )

            # Extract text response
            if not response or not response.choices:
                raise OCRProviderError("Empty response from OpenAI API")

            response_text = response.choices[0].message.content.strip()

            # Security: Log only metadata
            truncated_response = response_text[:100] + "..." if len(response_text) > 100 else response_text
            logger.debug(f"OpenAI response received (length: {len(response_text)} chars): {truncated_response}")

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

        except self.openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise OCRProviderError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            if isinstance(e, (OCRProviderError, FileNotFoundError, ValueError)):
                raise
            logger.error(f"Unexpected error during OpenAI OCR: {str(e)}")
            raise OCRProviderError(f"OpenAI OCR processing failed: {str(e)}")
