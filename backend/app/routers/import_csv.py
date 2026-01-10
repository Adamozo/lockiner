from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..schemas import MonthlyImportResponse, CSVImportResponse
from ..services.import_csv import (
    ImportService,
    ImportNotFoundError,
    InvalidMonthFormatError,
    MonthAlreadyImportedError,
    InvalidFileTypeError,
    FileTooLargeError,
    FileSaveError,
)

# ---------------------------------------

router = APIRouter(prefix="/api/v1/import", tags=["import"])

# ---------------------------------------


async def get_import_service(db: AsyncSession = Depends(get_db)) -> ImportService:
    return ImportService(db)

# ---------------------------------------


@router.post("/csv", response_model=CSVImportResponse, status_code=status.HTTP_201_CREATED)
async def import_csv(
    file: UploadFile = File(..., description="Bank statement CSV file"),
    month: str = Form(..., description="Month in YYYY-MM format"),
    service: ImportService = Depends(get_import_service),
):
    try:
        result = await service.import_csv(
            month=month,
            filename=file.filename,
            file_size=file.size if hasattr(file, "size") else None,
            file_read_func=file.read,
        )

        return CSVImportResponse(
            month=result["month"],
            imported_count=result["imported_count"],
            skipped_count=result["skipped_count"],
            errors=result["errors"],
        )

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except MonthAlreadyImportedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except InvalidFileTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except FileTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except FileSaveError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create import record: {str(e)}",
        )


@router.get("/history", response_model=List[MonthlyImportResponse])
async def get_import_history(
    skip: int = 0,
    limit: int = 100,
    service: ImportService = Depends(get_import_service),
):
    return await service.get_import_history(skip=skip, limit=limit)


@router.get("/history/{import_id}", response_model=MonthlyImportResponse)
async def get_import_details(
    import_id: int,
    service: ImportService = Depends(get_import_service),
):
    try:
        return await service.get_import_details(import_id)

    except ImportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/history/{import_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_import_record(
    import_id: int,
    service: ImportService = Depends(get_import_service),
):
    try:
        await service.delete_import_record(import_id)

    except ImportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete import record: {str(e)}",
        )


@router.get("/check/{month}")
async def check_month_imported(
    month: str,
    service: ImportService = Depends(get_import_service),
):
    try:
        return await service.check_month_imported(month)

    except InvalidMonthFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
