"""
Anthropic Claude Vision API provider for receipt OCR.

This module implements the OCR provider interface using Anthropic's Claude Vision API.
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


class ClaudeOCRProvider(BaseOCRProvider):
    """Anthropic Claude Vision API provider for receipt OCR."""

    def __init__(self, api_key: str):
        """
        Initialize Claude OCR provider.

        Args:
            api_key: Anthropic API key

        Raises:
            ValueError: If API key is invalid
        """
        super().__init__(api_key)

        # Validate that anthropic package is installed
        try:
            import anthropic
            self.anthropic = anthropic
        except ImportError:
            raise ValueError(
                "Anthropic package not installed. "
                "Install with: pip install anthropic"
            )

    @property
    def provider_name(self) -> str:
        """Get the human-readable name of this provider."""
        return "Anthropic Claude"

    @property
    def provider_type(self) -> OCRProvider:
        """Get the provider type enum."""
        return OCRProvider.CLAUDE

    def _encode_image(self, image_path: str) -> tuple[str, str]:
        """
        Encode image as base64 for Claude API.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (base64_data, media_type)
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

        return base64_data, media_type

    async def scan_receipt(self, image_path: str) -> Dict[str, Any]:
        """
        Scan receipt image using Anthropic Claude Vision API.

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
            base64_image, media_type = self._encode_image(image_path)
        except Exception as e:
            raise OCRProviderError(f"Failed to encode image: {str(e)}")

        # Get standard OCR prompt
        from .ocr_provider import get_ocr_prompt
        prompt = get_ocr_prompt()

        try:
            client = self.anthropic.Anthropic(api_key=self.api_key)

            logger.info(f"Processing receipt with Claude: {image_path}")

            # Call Claude API with vision
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                temperature=0.1,  # Low temperature for consistent extraction
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64_image,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            # Extract text response
            if not response or not response.content:
                raise OCRProviderError("Empty response from Claude API")

            # Get text from first content block
            response_text = response.content[0].text.strip()

            # Security: Log only metadata
            truncated_response = response_text[:100] + "..." if len(response_text) > 100 else response_text
            logger.debug(f"Claude response received (length: {len(response_text)} chars): {truncated_response}")

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

        except self.anthropic.APIError as e:
            logger.error(f"Claude API error: {str(e)}")
            raise OCRProviderError(f"Claude API error: {str(e)}")
        except Exception as e:
            if isinstance(e, (OCRProviderError, FileNotFoundError, ValueError)):
                raise
            logger.error(f"Unexpected error during Claude OCR: {str(e)}")
            raise OCRProviderError(f"Claude OCR processing failed: {str(e)}")
