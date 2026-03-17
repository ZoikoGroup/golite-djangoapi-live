"""
VCare API service — Django port of the React vcareAuth / vcareFetch utilities.

Token is cached in-process (module-level variable).
For multi-process deployments (gunicorn etc.) consider caching in Redis instead.
"""
import logging
import threading

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# In-process token cache (thread-safe)
# --------------------------------------------------------------------------- #
_token_lock = threading.Lock()
_cached_token: str | None = None

VCARE_BASE_URL = "https://www.vcareapi.com:8080"
VCARE_TOKEN_EXPIRED_CODE = "RESTAPI001"


def get_vcare_token(force_refresh: bool = False) -> str:
    """
    Authenticate with VCare and return a bearer token.
    Caches the token in memory; pass force_refresh=True to re-authenticate.
    """
    global _cached_token

    with _token_lock:
        if _cached_token and not force_refresh:
            return _cached_token

        payload = {
            "vendor_id": settings.VCARE_VENDOR_ID,
            "username": settings.VCARE_USERNAME,
            "password": settings.VCARE_PASSWORD,
            "pin": settings.VCARE_PIN,
        }

        try:
            response = requests.post(
                f"{VCARE_BASE_URL}/authenticate",
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("VCare authentication request failed: %s", exc)
            raise RuntimeError("VCare authentication request failed") from exc

        token = data.get("token")
        if not token:
            logger.error("VCare auth failed — response: %s", data)
            raise RuntimeError("VCare authentication failed: no token in response")

        _cached_token = token
        logger.info("VCare token refreshed successfully.")
        return _cached_token


def vcare_fetch(endpoint: str, body: dict) -> dict:
    """
    POST to a VCare endpoint.  Automatically retries once on token expiry
    (msg_code == RESTAPI001).

    Args:
        endpoint: Path segment, e.g. "inventory"
        body:     JSON-serialisable request payload

    Returns:
        Parsed JSON response as a dict.
    """
    token = get_vcare_token()

    def _post(tok: str) -> dict:
        try:
            resp = requests.post(
                f"{VCARE_BASE_URL}/{endpoint}",
                json=body,
                headers={"Content-Type": "application/json", "token": tok},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.error("VCare fetch error [%s]: %s", endpoint, exc)
            raise RuntimeError(f"VCare API request failed: {exc}") from exc

    data = _post(token)

    # Retry once on expired-token response
    if isinstance(data, dict) and data.get("msg_code") == VCARE_TOKEN_EXPIRED_CODE:
        logger.info("VCare token expired — refreshing and retrying.")
        new_token = get_vcare_token(force_refresh=True)
        data = _post(new_token)

    return data


# --------------------------------------------------------------------------- #
# Convenience wrapper — eSIM / device compatibility check
# --------------------------------------------------------------------------- #
def check_device_esim_compatibility(imei: str) -> dict:
    """
    Query VCare for eSIM compatibility of a given IMEI.
    Mirrors the React call: vcareFetch("inventory", { action: "get_query_device", ... })
    """
    return vcare_fetch(
        "inventory",
        {
            "action": "get_query_device",
            "carrier": "BLUECONNECTSATT",
            "source": "WEBSITE",
            "agent_id": "ewebsiteapi",
            "imei": str(imei),
        },
    )
