from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import (
    APIProviderConfigCreate,
    APIProviderConfigResponse,
    APIProviderListResponse,
    SetActiveProviderRequest,
)
from ..services.user_api_keys import UserAPIKeyService
from ..integrations.ocr_provider import OCRProvider

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


def get_api_key_service(db: AsyncSession = Depends(get_db)) -> UserAPIKeyService:
    return UserAPIKeyService(db)


async def get_user_active_ocr_provider(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> tuple[OCRProvider | None, str | None]:
    service = UserAPIKeyService(db)
    return await service.get_active_provider(current_user)


@router.post("/api-providers", status_code=status.HTTP_201_CREATED)
async def add_api_provider(
    config: APIProviderConfigCreate,
    current_user: User = Depends(get_current_user),
    service: UserAPIKeyService = Depends(get_api_key_service),
) -> APIProviderConfigResponse:
    try:
        provider_type = OCRProvider(config.provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {', '.join([p.value for p in OCRProvider])}",
        )

    result = await service.add_api_key(
        user=current_user,
        provider=provider_type,
        api_key=config.api_key,
        set_active=config.is_active or False,
    )

    return result


@router.get("/api-providers", response_model=APIProviderListResponse)
async def list_api_providers(
    current_user: User = Depends(get_current_user),
    service: UserAPIKeyService = Depends(get_api_key_service),
):
    return await service.list_providers(current_user)


@router.post("/active-provider", status_code=status.HTTP_200_OK)
async def set_active_provider(
    request: SetActiveProviderRequest,
    current_user: User = Depends(get_current_user),
    service: UserAPIKeyService = Depends(get_api_key_service),
):
    try:
        provider_type = OCRProvider(request.provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {', '.join([p.value for p in OCRProvider])}",
        )

    success = await service.set_active_provider(current_user, provider_type)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {request.provider} not configured. Add API key first.",
        )

    return {"message": f"Active provider set to {request.provider}"}


@router.delete("/api-providers/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_provider(
    provider: str,
    current_user: User = Depends(get_current_user),
    service: UserAPIKeyService = Depends(get_api_key_service),
):
    try:
        provider_type = OCRProvider(provider.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {', '.join([p.value for p in OCRProvider])}",
        )

    deleted = await service.delete_provider(current_user, provider_type)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )

    return None
