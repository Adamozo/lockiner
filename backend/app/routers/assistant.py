# =============================================================================
# PRZYGOTOWANIE POD BYCZEK CLOUD
#
# Ten endpoint działa jako proxy: Lockiner → Byczek Agent Service.
# Lokalny Byczek nie jest osiągalny z zewnątrz, więc endpoint zwróci 503
# dopóki BYCZQ_SERVICE_URL pozostaje pusty.
#
# Docelowa architektura z Byczek Cloud:
#   Klient → Lockiner /api/v1/assistant/chat → Byczek Cloud → lokalny Byczek
#
# Token OAuth użytkownika jest przekazywany do Byczka, który weryfikuje go
# przez Lockiner /oauth/userinfo — dzięki temu Byczek wie kim jest użytkownik.
# =============================================================================

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import get_settings
from ..dependencies import get_current_user
from ..models import User
from ..schemas.assistant import AssistantChatRequest, AssistantChatResponse

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])
security = HTTPBearer()


@router.post("/chat", response_model=AssistantChatResponse)
async def chat(
    body: AssistantChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
):
    """Proxy do Byczq Agent Service. Token użytkownika przekazywany dalej."""
    settings = get_settings()
    if not settings.byczq_service_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Byczq service not configured",
        )

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.byczq_service_url}/chat",
                json=body.model_dump(),
                headers={"Authorization": f"Bearer {credentials.credentials}"},
                timeout=30.0,
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Byczq service unreachable",
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Byczq service error",
        )

    return AssistantChatResponse(**resp.json())
