from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timezone
from pathlib import Path
import os
import uuid
import json
import logging

from ..models import Receipt, Transaction
from ..schemas import ReceiptUpdate, ReceiptOCRResponse
from ..repositories.receipt import ReceiptRepository
from ..repositories.household import HouseholdRepository
from ..integrations.ocr_provider import create_ocr_provider, OCRProviderError, OCRProvider
from .ownership import OwnershipService
from .food import FoodService

logger = logging.getLogger(__name__)

# ---------------------------------------

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/uploads"))
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# ---------------------------------------


class ReceiptNotFoundError(Exception):
    def __init__(self, receipt_id: int):
        self.receipt_id = receipt_id
        super().__init__(f"Receipt {receipt_id} not found")


class TransactionNotFoundError(Exception):
    def __init__(self, transaction_id: int):
        self.transaction_id = transaction_id
        super().__init__(f"Transaction {transaction_id} not found")


class InvalidFileTypeError(Exception):
    def __init__(self, extension: str):
        self.extension = extension
        super().__init__(f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")


class FileTooLargeError(Exception):
    def __init__(self, size: int):
        self.size = size
        max_mb = MAX_FILE_SIZE // (1024 * 1024)
        super().__init__(f"File too large ({size} bytes). Maximum size: {max_mb} MB")


class EmptyFileError(Exception):
    def __init__(self):
        super().__init__("Empty file uploaded (0 bytes)")


class FileReadError(Exception):
    def __init__(self):
        super().__init__("Failed to read uploaded file")


class FileSaveError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Failed to save file: {message}")


class InvalidFilenameError(Exception):
    def __init__(self):
        super().__init__("Invalid filename")


class ImageNotFoundError(Exception):
    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"Image file not found: {filename}")


class ReceiptAccessDeniedError(Exception):
    def __init__(self, receipt_id: int):
        self.receipt_id = receipt_id
        super().__init__(f"Access denied to receipt {receipt_id}")


# ---------------------------------------


class ReceiptService:
    def __init__(self, db: AsyncSession):
        self.repository: ReceiptRepository = ReceiptRepository(db)
        self.household_repository: HouseholdRepository = HouseholdRepository(db)
        self.ownership_service: OwnershipService = OwnershipService(db)
        self.db = db

    async def _resolve_household_id(self, household_uid: Optional[str]) -> Optional[int]:
        """Convert household UID (string) to household ID (int)."""
        if not household_uid:
            return None
        household = await self.household_repository.get_by_uid(household_uid)
        return household.id if household else None

    async def _get_accessible_receipt_ids(
        self,
        user_id: int,
        household_id: Optional[int] = None,
    ) -> List[int]:
        """Get IDs of receipts accessible to user (personal + optional household)."""
        user_ids = await self.ownership_service.get_user_entity_ids("receipt", user_id)

        if household_id:
            household_ids = await self.ownership_service.get_household_entity_ids(
                "receipt", household_id
            )
            return list(set(user_ids + household_ids))

        return user_ids

    async def _check_access(
        self,
        receipt_id: int,
        user_id: int,
        household_id: Optional[int] = None,
    ) -> bool:
        """Check if user has access to a receipt."""
        if await self.ownership_service.user_owns_entity("receipt", receipt_id, user_id):
            return True

        if household_id:
            if await self.ownership_service.household_owns_entity(
                "receipt", receipt_id, household_id
            ):
                return True

        return False

    async def list_receipts(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        verified: Optional[bool] = None,
        household_uid: Optional[str] = None,
    ) -> list[Receipt]:
        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        accessible_ids = await self._get_accessible_receipt_ids(user_id, household_id)
        return await self.repository.get_all(
            skip=skip,
            limit=limit,
            verified=verified,
            receipt_ids=accessible_ids,
        )

    async def get_receipt(
        self,
        receipt_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> Receipt:
        receipt = await self.repository.get_by_id(receipt_id)
        if receipt is None:
            raise ReceiptNotFoundError(receipt_id)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        if not await self._check_access(receipt_id, user_id, household_id):
            raise ReceiptAccessDeniedError(receipt_id)

        return receipt

    async def validate_image_file(self, filename: str, read_file_func) -> bytes:
        """Validate uploaded image file and return content."""
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(file_ext)

        try:
            content = await read_file_func()

        except Exception:
            raise FileReadError()

        if len(content) == 0:
            raise EmptyFileError()

        if len(content) > MAX_FILE_SIZE:
            raise FileTooLargeError(len(content))

        logger.info(f"File validated: {filename} ({len(content)} bytes, extension: {file_ext})")
        return content

    async def save_upload_file(self, content: bytes, original_filename: str) -> str:
        """Save uploaded file content to disk."""
        try:
            file_ext = Path(original_filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_DIR / unique_filename

            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(f"Saved file: {unique_filename} ({len(content)} bytes)")
            return unique_filename

        except Exception as e:
            raise FileSaveError(str(e))

    async def upload_receipt(
        self,
        file_content: bytes,
        original_filename: str,
        scan_date: Optional[str],
        provider_type: Optional[OCRProvider],
        api_key: Optional[str],
        user_id: int,
        household_id: Optional[int] = None,
    ) -> tuple[Receipt, Optional[ReceiptOCRResponse], Optional[str]]:
        """Upload receipt image and perform OCR extraction."""
        image_path = await self.save_upload_file(file_content, original_filename)
        full_image_path = UPLOAD_DIR / image_path

        if not scan_date:
            scan_date = datetime.now(timezone.utc).date().isoformat()

        ocr_data = None
        ocr_error = None

        if provider_type and api_key:
            try:
                ocr_provider = create_ocr_provider(provider_type, api_key)
                ocr_result = await ocr_provider.scan_receipt(str(full_image_path))

                if ocr_result.get("date"):
                    scan_date = ocr_result["date"]

                db_receipt = Receipt(
                    image_path=image_path,
                    scan_date=scan_date,
                    merchant=ocr_result.get("merchant"),
                    total=ocr_result.get("total"),
                    payment_method=ocr_result.get("payment_method"),
                    items_json=json.dumps(ocr_result.get("items", []), ensure_ascii=False),
                    raw_ocr_response=json.dumps(ocr_result, ensure_ascii=False),
                    verified=False,
                )

                ocr_data = ReceiptOCRResponse(**ocr_result)

            except OCRProviderError as e:
                logger.warning(f"OCR failed for {image_path} (provider: {provider_type.value}): {str(e)}")
                ocr_error = str(e)
                db_receipt = Receipt(
                    image_path=image_path,
                    scan_date=scan_date,
                    merchant=None,
                    total=None,
                    items_json=None,
                    raw_ocr_response=json.dumps({"error": str(e)}, ensure_ascii=False),
                    verified=False,
                )

            except ValueError as e:
                logger.error(f"Value error during OCR: {str(e)}")
                ocr_error = f"Invalid data: {str(e)}"
                db_receipt = Receipt(
                    image_path=image_path,
                    scan_date=scan_date,
                    merchant=None,
                    total=None,
                    items_json=None,
                    raw_ocr_response=json.dumps({"error": str(e)}, ensure_ascii=False),
                    verified=False,
                )

            except ConnectionError as e:
                logger.error(f"Connection error during OCR: {str(e)}")
                ocr_error = f"Connection error: {str(e)}"
                db_receipt = Receipt(
                    image_path=image_path,
                    scan_date=scan_date,
                    merchant=None,
                    total=None,
                    items_json=None,
                    raw_ocr_response=json.dumps({"error": "Connection error"}, ensure_ascii=False),
                    verified=False,
                )

            except Exception as e:
                logger.exception(f"Unexpected error during OCR for {image_path}: {str(e)}")
                ocr_error = f"OCR processing failed: {str(e)}"
                db_receipt = Receipt(
                    image_path=image_path,
                    scan_date=scan_date,
                    merchant=None,
                    total=None,
                    items_json=None,
                    raw_ocr_response=json.dumps({"error": "Unexpected error"}, ensure_ascii=False),
                    verified=False,
                )
        else:
            ocr_error = "Gemini API key not configured. Please save your API key via POST /api/v1/settings/gemini-key"
            db_receipt = Receipt(
                image_path=image_path,
                scan_date=scan_date,
                merchant=None,
                total=None,
                items_json=None,
                raw_ocr_response=None,
                verified=False,
            )

        try:
            created_receipt = await self.repository.create(db_receipt)

            # Create ownership record
            if household_id:
                await self.ownership_service.assign_to_household(
                    "receipt", created_receipt.id, household_id, added_by=user_id
                )
            else:
                await self.ownership_service.assign_to_user("receipt", created_receipt.id, user_id)

            return created_receipt, ocr_data, ocr_error

        except Exception as e:
            await self.db.rollback()
            try:
                os.remove(full_image_path)
            except:
                pass
            raise

    async def update_receipt(
        self,
        receipt_id: int,
        data: ReceiptUpdate,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> Receipt:
        receipt = await self.repository.get_by_id(receipt_id)
        if receipt is None:
            raise ReceiptNotFoundError(receipt_id)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        if not await self._check_access(receipt_id, user_id, household_id):
            raise ReceiptAccessDeniedError(receipt_id)

        is_being_verified = data.verified is True and not receipt.verified

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(receipt, field, value)

        if is_being_verified and receipt.total is not None:
            existing_transaction = await self.repository.get_transaction_by_receipt_id(receipt_id)

            if existing_transaction is None:
                transaction = Transaction(
                    date=receipt.scan_date,
                    amount=-abs(receipt.total),
                    description=f"{receipt.merchant or 'Receipt purchase'}",
                    category=receipt.category or "Inne",
                    payment_method=receipt.payment_method,
                    receipt_id=receipt_id,
                    notes="Auto-created from verified receipt",
                )
                self.db.add(transaction)

                # Also create ownership for the auto-created transaction
                await self.db.flush()  # Get the transaction ID
                if household_id:
                    await self.ownership_service.assign_to_household(
                        "transaction", transaction.id, household_id, added_by=user_id
                    )
                else:
                    await self.ownership_service.assign_to_user("transaction", transaction.id, user_id)

                logger.info(f"Created transaction for verified receipt {receipt_id}: {receipt.merchant}, {receipt.total} PLN")

        # Trigger food import when receipt is verified and has items
        if is_being_verified and receipt.items_json:
            try:
                items = json.loads(receipt.items_json)
                if items:
                    food_service = FoodService(self.db)
                    await food_service.create_pending_import_from_receipt(
                        receipt_id=receipt.id,
                        items=items,
                        user_id=user_id,
                        household_id=household_id,
                    )
                    logger.info(f"Created food pending import for receipt {receipt_id} with {len(items)} items")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse items_json for receipt {receipt_id}: {e}")
            except Exception as e:
                logger.warning(f"Failed to create food import for receipt {receipt_id}: {e}")
                # Don't fail the whole verification if food import fails

        try:
            return await self.repository.update(receipt)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update receipt {receipt_id}: {str(e)}")
            raise

    async def delete_receipt(
        self,
        receipt_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> None:
        receipt = await self.repository.get_by_id(receipt_id)
        if receipt is None:
            raise ReceiptNotFoundError(receipt_id)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        if not await self._check_access(receipt_id, user_id, household_id):
            raise ReceiptAccessDeniedError(receipt_id)

        image_path = UPLOAD_DIR / receipt.image_path
        try:
            if image_path.exists():
                os.remove(image_path)

        except Exception as e:
            logger.warning(f"Failed to delete image file {image_path}: {e}")

        await self.repository.delete(receipt)

    async def link_receipt_to_transaction(
        self,
        receipt_id: int,
        transaction_id: int,
        user_id: int,
        household_uid: Optional[str] = None,
    ) -> Receipt:
        receipt = await self.repository.get_by_id(receipt_id)
        if receipt is None:
            raise ReceiptNotFoundError(receipt_id)

        # Convert household UID to ID
        household_id = await self._resolve_household_id(household_uid)

        if not await self._check_access(receipt_id, user_id, household_id):
            raise ReceiptAccessDeniedError(receipt_id)

        transaction = await self.repository.get_transaction_by_id(transaction_id)
        if transaction is None:
            raise TransactionNotFoundError(transaction_id)

        transaction.receipt_id = receipt_id
        await self.repository.save()

        return receipt

    def get_image_path(self, filename: str) -> Path:
        """Get validated image file path."""
        if not filename or ".." in filename or "/" in filename or "\\" in filename:
            raise InvalidFilenameError()

        file_path = UPLOAD_DIR / filename

        if not file_path.exists() or not file_path.is_file():
            raise ImageNotFoundError(filename)

        return file_path

    def get_media_type(self, filename: str) -> str:
        """Get media type from filename extension."""
        file_ext = Path(filename).suffix.lower()
        media_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".heic": "image/heic",
        }
        return media_type_map.get(file_ext, "application/octet-stream")
