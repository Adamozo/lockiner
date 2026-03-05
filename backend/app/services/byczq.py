# =============================================================================
# PRZYGOTOWANIE POD BYCZEK CLOUD
#
# Lokalny Byczek działa w sieci domowej użytkownika i nie jest osiągalny
# z zewnątrz (NAT, brak publicznego IP). Dlatego ten moduł jest obecnie
# bezfunkcyjny — Lockiner nie może wykonać połączenia HTTP do lokalnego Byczka.
#
# Docelowa architektura z Byczek Cloud:
#   Lockiner → HTTP push → Byczek Cloud (relay) → WebSocket → lokalny Byczek
#
# Gdy BYCZQ_SERVICE_URL jest pusty (domyślnie), forward_notification()
# kończy się natychmiast bez efektów ubocznych.
# =============================================================================

import logging
import httpx
from ..config import get_settings

logger = logging.getLogger(__name__)


async def forward_notification(title: str, body: str, user_id: int | None = None) -> None:
    settings = get_settings()
    if not settings.byczq_service_url or not settings.byczq_notify_secret:
        return

    payload = {"title": title, "body": body}
    if user_id is not None:
        payload["user_id"] = str(user_id)

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.byczq_service_url}/notify",
                json=payload,
                headers={"X-Notify-Secret": settings.byczq_notify_secret},
                timeout=3.0,
            )
    except Exception as e:
        logger.warning(f"Failed to forward notification to Byczq: {e}")
