from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel


class BulkDeleteRequest(BaseModel):
    ids: List[int]

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import TransactionCreate, TransactionUpdate, TransactionResponse
from ..services.transaction import (
    TransactionService,
    TransactionNotFoundError,
    TransactionAccessDeniedError,
    InvalidDateFormatError,
)

# ---------------------------------------

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

# ---------------------------------------


async def get_transaction_service(db: AsyncSession = Depends(get_db)) -> TransactionService:
    return TransactionService(db)

# ---------------------------------------


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM format)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in description and notes"),
    min_amount: Optional[float] = Query(None, description="Minimum amount (negative for expenses)"),
    max_amount: Optional[float] = Query(None, description="Maximum amount"),
    household_id: Optional[str] = Query(None, description="Include transactions from household (UUID)"),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.list_transactions(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        month=month,
        category=category,
        search=search,
        min_amount=min_amount,
        max_amount=max_amount,
        household_uid=household_id,
    )


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    household_id: Optional[str] = Query(None, description="Assign to household instead of personal (UUID)"),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return await service.create_transaction(
            transaction,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except InvalidDateFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    household_id: Optional[str] = Query(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return await service.get_transaction(
            transaction_id,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except TransactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except TransactionAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    household_id: Optional[str] = Query(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return await service.update_transaction(
            transaction_id,
            transaction_update,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except TransactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except TransactionAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_transactions(
    body: BulkDeleteRequest,
    household_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    deleted = 0
    errors = []
    for transaction_id in body.ids:
        try:
            await service.delete_transaction(
                transaction_id,
                user_id=current_user.id,
                household_uid=household_id,
            )
            deleted += 1
        except (TransactionNotFoundError, TransactionAccessDeniedError) as e:
            errors.append(str(e))
    return {"deleted": deleted, "errors": errors}


@router.post("/import-pdf", status_code=status.HTTP_200_OK)
async def import_bank_pdf(
    file: UploadFile = File(...),
    bank: str = Query(..., description="Bank identifier: 'velobank' | 'millennium'"),
    household_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 20 MB)")

    try:
        result = await service.import_bank_pdf(
            pdf_bytes=pdf_bytes,
            bank=bank,
            user_id=current_user.id,
            household_uid=household_id,
        )
        return {"imported": result["imported"], "failed": result["skipped"], "errors": result["errors"]}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Failed to parse PDF: {str(exc)}")


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    household_id: Optional[str] = Query(None, description="Check household access (UUID)"),
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        await service.delete_transaction(
            transaction_id,
            user_id=current_user.id,
            household_uid=household_id,
        )

    except TransactionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except TransactionAccessDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
