from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from pathlib import Path
import os
import uuid

from ..models import MonthlyImport
from ..repositories.import_csv import ImportRepository

# ---------------------------------------

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/uploads"))
CSV_DIR = UPLOAD_DIR / "csv"
ALLOWED_EXTENSIONS = {".csv", ".txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# ---------------------------------------


class ImportNotFoundError(Exception):
    def __init__(self, import_id: int):
        self.import_id = import_id
        super().__init__(f"Import record {import_id} not found")


class InvalidMonthFormatError(Exception):
    def __init__(self):
        super().__init__("Invalid month format. Use YYYY-MM (e.g., '2024-01')")


class MonthAlreadyImportedError(Exception):
    def __init__(self, month: str, imported_at: str):
        self.month = month
        self.imported_at = imported_at
        super().__init__(f"Month {month} was already imported on {imported_at}")


class InvalidFileTypeError(Exception):
    def __init__(self):
        super().__init__(f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")


class FileTooLargeError(Exception):
    def __init__(self):
        max_mb = MAX_FILE_SIZE // (1024 * 1024)
        super().__init__(f"File too large. Maximum size: {max_mb} MB")


class FileSaveError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Failed to save file: {message}")


# ---------------------------------------


class ImportService:
    def __init__(self, db: AsyncSession):
        self.repository: ImportRepository = ImportRepository(db)
        self.db = db

    def _validate_month(self, month: str) -> None:
        try:
            datetime.strptime(month, "%Y-%m")

        except ValueError:
            raise InvalidMonthFormatError()

    def validate_csv_file(self, filename: str, file_size: Optional[int]) -> None:
        """Validate uploaded CSV file."""
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError()

        if file_size is not None and file_size > MAX_FILE_SIZE:
            raise FileTooLargeError()

    async def save_csv_file(self, file_read_func, original_filename: str) -> str:
        """Save uploaded CSV file to disk."""
        try:
            CSV_DIR.mkdir(parents=True, exist_ok=True)

            file_ext = Path(original_filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = CSV_DIR / unique_filename

            content = await file_read_func()
            with open(file_path, "wb") as f:
                f.write(content)

            return str(file_path)

        except Exception as e:
            raise FileSaveError(str(e))

    async def get_import_history(self, skip: int = 0, limit: int = 100) -> list[MonthlyImport]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def get_import_details(self, import_id: int) -> MonthlyImport:
        import_record = await self.repository.get_by_id(import_id)
        if import_record is None:
            raise ImportNotFoundError(import_id)

        return import_record

    async def check_month_imported(self, month: str) -> dict:
        """Check if a month has already been imported."""
        self._validate_month(month)

        import_record = await self.repository.get_by_month(month)

        if import_record:
            return {
                "month": month,
                "imported": True,
                "import_date": import_record.imported_at,
                "filename": import_record.filename,
                "transactions_count": import_record.transactions_count,
            }

        return {
            "month": month,
            "imported": False,
        }

    async def import_csv(
        self,
        month: str,
        filename: str,
        file_size: Optional[int],
        file_read_func,
    ) -> dict:
        """Import transactions from a bank statement CSV file."""
        self._validate_month(month)

        existing_import = await self.repository.get_by_month(month)
        if existing_import:
            raise MonthAlreadyImportedError(month, existing_import.imported_at)

        self.validate_csv_file(filename, file_size)

        file_path = await self.save_csv_file(file_read_func, filename)

        # TODO: Implement CSV parsing logic here
        imported_count = 0
        skipped_count = 0
        errors = ["CSV parsing not yet implemented - this is a placeholder"]

        db_import = MonthlyImport(
            month=month,
            filename=filename,
            transactions_count=imported_count,
        )

        try:
            await self.repository.create(db_import)

            return {
                "month": month,
                "imported_count": imported_count,
                "skipped_count": skipped_count,
                "errors": errors,
            }

        except Exception as e:
            await self.db.rollback()
            try:
                os.remove(file_path)
            except:
                pass
            raise

    async def delete_import_record(self, import_id: int) -> None:
        """Delete an import record."""
        import_record = await self.repository.get_by_id(import_id)
        if import_record is None:
            raise ImportNotFoundError(import_id)

        await self.repository.delete(import_record)
