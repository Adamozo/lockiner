"""Admin panel router - requires admin role."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..dependencies import require_admin
from ..models import User
from ..schemas.admin import (
    VoucherAdminResponse,
    VoucherGenerateRequest,
    VoucherGenerateResponse,
    UserAdminResponse,
    SetRoleRequest,
)
from ..services.admin import (
    AdminService,
    VoucherNotFoundError,
    CannotUnblockUsedVoucherError,
    UserNotFoundError,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


async def get_admin_service(db: AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(db)


# ============================================================================
# Voucher Endpoints
# ============================================================================

@router.get("/vouchers", response_model=List[VoucherAdminResponse])
async def list_vouchers(
    admin: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    """List all vouchers with details."""
    return await service.get_all_vouchers()


@router.post("/vouchers/generate", response_model=VoucherGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_vouchers(
    data: VoucherGenerateRequest,
    admin: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Generate new voucher codes."""
    vouchers = await service.generate_vouchers(data.count)
    return VoucherGenerateResponse(
        vouchers=[
            VoucherAdminResponse(
                id=v.id,
                code=v.code,
                status=v.status,
                used_by_user_id=v.used_by_user_id,
                used_at=v.used_at,
                created_at=v.created_at,
            )
            for v in vouchers
        ],
        count=len(vouchers),
    )


@router.put("/vouchers/{voucher_id}/block", response_model=VoucherAdminResponse)
async def block_voucher(
    voucher_id: int,
    admin: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Block a voucher."""
    try:
        v = await service.block_voucher(voucher_id)
        return VoucherAdminResponse(
            id=v.id, code=v.code, status=v.status,
            used_by_user_id=v.used_by_user_id, used_at=v.used_at, created_at=v.created_at,
        )
    except VoucherNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/vouchers/{voucher_id}/unblock", response_model=VoucherAdminResponse)
async def unblock_voucher(
    voucher_id: int,
    admin: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Unblock a voucher (only if not used)."""
    try:
        v = await service.unblock_voucher(voucher_id)
        return VoucherAdminResponse(
            id=v.id, code=v.code, status=v.status,
            used_by_user_id=v.used_by_user_id, used_at=v.used_at, created_at=v.created_at,
        )
    except VoucherNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CannotUnblockUsedVoucherError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================================================
# User Endpoints
# ============================================================================

@router.get("/users", response_model=List[UserAdminResponse])
async def list_users(
    admin: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    """List all users."""
    users = await service.get_all_users()
    return [
        UserAdminResponse(
            id=u.id, name=u.name, role=u.role,
            is_active=u.is_active, created_at=u.created_at,
        )
        for u in users
    ]


@router.put("/users/{user_id}/block", response_model=UserAdminResponse)
async def block_user(
    user_id: int,
    admin: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Deactivate a user."""
    try:
        u = await service.block_user(user_id)
        return UserAdminResponse(
            id=u.id, name=u.name, role=u.role,
            is_active=u.is_active, created_at=u.created_at,
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/users/{user_id}/unblock", response_model=UserAdminResponse)
async def unblock_user(
    user_id: int,
    admin: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Reactivate a user."""
    try:
        u = await service.unblock_user(user_id)
        return UserAdminResponse(
            id=u.id, name=u.name, role=u.role,
            is_active=u.is_active, created_at=u.created_at,
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/users/{user_id}/set-role", response_model=UserAdminResponse)
async def set_user_role(
    user_id: int,
    data: SetRoleRequest,
    admin: User = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
):
    """Change user role."""
    try:
        u = await service.set_user_role(user_id, data.role)
        return UserAdminResponse(
            id=u.id, name=u.name, role=u.role,
            is_active=u.is_active, created_at=u.created_at,
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
