"""
API endpoint: /api/device_compatibility_checker/

Authentication flow
-------------------
Every request must carry the registered secret key either:
  • HTTP header  X-Secret-Key: <key>          (recommended)
  • POST body    { ..., "secret_key": "<key>" }

The Origin / Referer header is cross-checked against the registered site_url
for the supplied secret key, providing a second layer of validation.
"""
import logging

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import ESIMCheckerEndpoint
from .vcare_service import check_device_esim_compatibility

logger = logging.getLogger(__name__)


def _extract_origin(request) -> str:
    """Return the calling origin from Origin or Referer header."""
    origin = request.META.get("HTTP_ORIGIN", "")
    if not origin:
        referer = request.META.get("HTTP_REFERER", "")
        # Strip path — keep scheme + host only
        if referer:
            from urllib.parse import urlparse
            p = urlparse(referer)
            origin = f"{p.scheme}://{p.netloc}"
    return origin.rstrip("/")


def _normalise_url(url: str) -> str:
    return url.rstrip("/")


@method_decorator(csrf_exempt, name='dispatch')
class DeviceCompatibilityCheckerView(View):

    def post(self, request, *args, **kwargs):
        import json

        # ------------------------------------------------------------------ #
        # 1. Parse request body
        # ------------------------------------------------------------------ #
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, Exception):
            return JsonResponse({"error": "Invalid JSON body."}, status=400)

        action = body.get("action", "")
        imei = body.get("imei") or body.get("imie")  # tolerate both spellings

        # ------------------------------------------------------------------ #
        # 2. Extract secret key (header takes priority over body)
        # ------------------------------------------------------------------ #
        secret_key = (
            request.META.get("HTTP_X_SECRET_KEY")
            or body.get("secret_key", "")
        )
        if not secret_key:
            return JsonResponse(
                {"error": "Missing secret key. Pass X-Secret-Key header or secret_key in body."},
                status=401,
            )

        # ------------------------------------------------------------------ #
        # 3. Look up registered endpoint
        # ------------------------------------------------------------------ #
        try:
            endpoint = ESIMCheckerEndpoint.objects.get(secret_key=secret_key)
        except ESIMCheckerEndpoint.DoesNotExist:
            logger.warning("API call with unknown secret key: %s", secret_key)
            return JsonResponse({"error": "Invalid secret key."}, status=401)

        if not endpoint.is_active:
            return JsonResponse(
                {"error": "This endpoint has been deactivated. Contact the administrator."},
                status=403,
            )

        # ------------------------------------------------------------------ #
        # 4. Origin / Referer validation
        # ------------------------------------------------------------------ #
        calling_origin = _extract_origin(request)
        registered_origin = _normalise_url(endpoint.site_url)

        if calling_origin and calling_origin != registered_origin:
            logger.warning(
                "Origin mismatch for key %s: expected %s, got %s",
                secret_key, registered_origin, calling_origin,
            )
            return JsonResponse(
                {"error": "Origin not allowed."},
                status=403,
            )

        # ------------------------------------------------------------------ #
        # 5. Validate action + IMEI
        # ------------------------------------------------------------------ #
        if action != "esim_checker":
            return JsonResponse(
                {"error": f"Unknown action '{action}'. Supported: esim_checker"},
                status=400,
            )

        if not imei:
            return JsonResponse({"error": "Missing 'imei' field."}, status=400)

        # ------------------------------------------------------------------ #
        # 6. Call VCare API
        # ------------------------------------------------------------------ #
        try:
            result = check_device_esim_compatibility(str(imei))
        except RuntimeError as exc:
            logger.error("VCare API error for IMEI %s: %s", imei, exc)
            return JsonResponse(
                {"error": "Upstream API error. Please try again later."},
                status=502,
            )

        # ------------------------------------------------------------------ #
        # 7. Record hit and return result
        # ------------------------------------------------------------------ #
        endpoint.increment_hits()

        # Parse nested VCare response
        device_status = (
            result.get("data", {})
            .get("RESULT", {})
            .get("responseDetails", {})
            .get("inquireDeviceStatusResponse", {})
            .get("deviceStatusDetails", {})
        )
        manufacturer = device_status.get("manufacturer", {})
        att_compatibility = device_status.get("attCompatibility", "RED")

        return JsonResponse({
            "success": True,
            "imei": imei,
            "esimCompatible": att_compatibility == "GREEN",
            "compatible": att_compatibility == "GREEN",
            "device": manufacturer.get("model"),
            "manufacturer": manufacturer.get("make"),
            "lteCompatible": device_status.get("umtsCapableIndicator") == "true",
            "blacklisted": device_status.get("blacklistedIndicator") == "Y",
            "deviceCategory": device_status.get("deviceCategory"),
            "message": "Device is compatible." if att_compatibility == "GREEN" else "Device is not compatible with our network.",
        })

    def options(self, request, *args, **kwargs):
        """Handle CORS preflight."""
        response = JsonResponse({})
        _add_cors_headers(response, request)
        return response


def _add_cors_headers(response, request):
    origin = request.META.get("HTTP_ORIGIN", "")
    if origin:
        # Only echo back origins that are registered + active
        if ESIMCheckerEndpoint.objects.filter(
            site_url__icontains=origin.replace("https://", "").replace("http://", ""),
            is_active=True,
        ).exists():
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, X-Secret-Key"
            response["Access-Control-Max-Age"] = "86400"
    return response
