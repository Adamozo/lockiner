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


def _get_byczq_url_and_secret() -> tuple[str, str]:
    """Pobiera URL i secret z DB (priorytet) lub env."""
    from .settings import SettingsService
    svc = SettingsService()
    url = svc.get_byczq_service_url()
    secret = svc.get_byczq_notify_secret()
    if not secret:
        secret = get_settings().byczq_notify_secret
    return url, secret


async def forward_notification(title: str, body: str, user_id: int | None = None) -> None:
    url, secret = _get_byczq_url_and_secret()
    if not url or not secret:
        return

    payload: dict = {"title": title, "body": body}
    if user_id is not None:
        payload["user_id"] = str(user_id)

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{url}/notify",
                json=payload,
                headers={"X-Notify-Secret": secret},
                timeout=3.0,
            )
    except Exception as e:
        logger.warning(f"Failed to forward notification to Byczq: {e}")
