from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import ReceiptUpdate, ReceiptResponse, ReceiptUploadResponse
from ..services.receipt import (
    ReceiptService,
    ReceiptNotFoundError,
    ReceiptAccessDeniedError,
    TransactionNotFoundError,
    InvalidFileTypeError,
    FileTooLargeError,
    EmptyFileError,
    FileReadError,
    FileSaveError,
    InvalidFilenameError,
    ImageNotFoundError,
)
from ..services.user_api_keys import UserAPIKeyService

# ---------------------------------------

router = APIRouter(prefix="/api/v1/receipts", tags=["receipts"])

# ---------------------------------------


async def get_receipt_service(db: AsyncSession = Depends(get_db)) -> ReceiptService:
    return ReceiptService(db)

# ---------------------------------------


@router.post("/upload", response_model=ReceiptUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_receipt(
    file: UploadFile = File(..., description="Receipt image file"),
    scan_date: Optional[str] = Form(None, description="Receipt date (YYYY-MM-DD)"),
    household_id: Optional[int] = Form(None, description="Assign to household instead of personal"),
    current_user: User = Depends(get_current_user),
    service: ReceiptService = Depends(get_receipt_service),
    db: AsyncSession = Depends(get_db),
):
    try:
        file_content = await service.validate_image_file(file.filename, file.read)

    except InvalidFileTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except EmptyFileError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except FileTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except FileReadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    api_key_service = UserAPIKeyService(db)
    provider_type, api_key = await api_key_service.get_active_provider(current_user)

    try:
        receipt, ocr_data, ocr_error = await service.upload_receipt(
            file_content=file_content,
            original_filename=file.filename,
            scan_date=scan_date,
            provider_type=provider_type,
            api_key=api_key,
            user_id=current_user.id,
            household_id=household_id,
        )

        return ReceiptUploadResponse(
            receipt_id=receipt.id,
            image_path=receipt.image_path,
            ocr_data=ocr_data,
            error=ocr_error,
            created_at=receipt.created_at,
        )

    except FileSaveError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Receipt upload failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create receipt: {str(e)}",
        )


@router.get("/", response_model=List[ReceiptResponse])
async def list_receipts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    verified: Optional[bool] = Query(None, description="Filter by verified status"),
    household_id: Optional[str] = Query(None, description="Include receipts from household (UUID)"),
    current_user: User = Depends(get_current_user),
    service: ReceiptService = Depends(get_receipt_service),
):
    return await service.list_receipts(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        verified=verified,
        household_uid=household_id,
    )


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: int,
    household_id: Optional[str] = Query(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: ReceiptService = Depends(get_receipt_service),
):
    try:
        return await service.get_receipt(
            receipt_id,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except ReceiptNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except ReceiptAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/images/{filename}")
async def get_receipt_image(
    filename: str,
    service: ReceiptService = Depends(get_receipt_service),
):
    try:
        file_path = service.get_image_path(filename)
        media_type = service.get_media_type(filename)

        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=filename,
        )

    except InvalidFilenameError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except ImageNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{receipt_id}", response_model=ReceiptResponse)
async def update_receipt(
    receipt_id: int,
    receipt_update: ReceiptUpdate,
    household_id: Optional[str] = Query(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: ReceiptService = Depends(get_receipt_service),
):
    try:
        return await service.update_receipt(
            receipt_id,
            receipt_update,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except ReceiptNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except ReceiptAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update receipt: {str(e)}",
        )


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receipt(
    receipt_id: int,
    household_id: Optional[str] = Query(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: ReceiptService = Depends(get_receipt_service),
):
    try:
        await service.delete_receipt(
            receipt_id,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except ReceiptNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except ReceiptAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete receipt: {str(e)}",
        )


@router.post("/{receipt_id}/images", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def add_receipt_image(
    receipt_id: int,
    file: UploadFile = File(..., description="Additional receipt image file"),
    household_id: Optional[str] = Form(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: ReceiptService = Depends(get_receipt_service),
):
    try:
        file_content = await service.validate_image_file(file.filename, file.read)

    except (InvalidFileTypeError, EmptyFileError, FileTooLargeError, FileReadError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        return await service.add_receipt_image(
            receipt_id=receipt_id,
            file_content=file_content,
            original_filename=file.filename,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except ReceiptNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ReceiptAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except FileSaveError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{receipt_id}/link", response_model=ReceiptResponse)
async def link_receipt_to_transaction(
    receipt_id: int,
    transaction_id: int = Query(..., description="Transaction ID to link"),
    household_id: Optional[str] = Query(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: ReceiptService = Depends(get_receipt_service),
):
    try:
        return await service.link_receipt_to_transaction(
            receipt_id,
            transaction_id,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except ReceiptNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except ReceiptAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except TransactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link receipt: {str(e)}",
        )
