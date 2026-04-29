"""
API endpoint: /api/device_compatibility_checker/

Authentication flow
-------------------
Every request must carry the registered secret key either:
  • HTTP header  X-Secret-Key: <key>          (recommended)
  • POST body    { ..., "secret_key": "<key>" }

The Origin / Referer header is cross-checked against the registered site_url
for the supplied secret key, providing a second layer of validation.

Supported actions
-----------------
esim_check
    Only checks the ESIMCheckerLog table for the IMEI.
    HIT  → return compatible=true.
    MISS → return compatible=false.
    No VCare API call is made.

esim_update
    Insert the IMEI into ESIMCheckerLog table (hit_count=1).
    If the IMEI already exists, increment hit_count instead.
    No VCare API call is made.

esim_v_check
    1. Check ESIMCheckerLog table first (cache lookup).
       HIT  → increment hit_count, return compatible=true (source: cache). No VCare call.
       MISS → call VCare API (check_device_esim_compatibility).
    2. If VCare returns attCompatibility == "GREEN" → insert IMEI into
       ESIMCheckerLog and return the full VCare response (source: vcare).
    3. Otherwise → return compatible=false with the full VCare response. No DB write.
"""
import logging

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import ESIMCheckerEndpoint, ESIMCheckerLog
from .vcare_service import check_device_esim_compatibility

logger = logging.getLogger(__name__)

# VCare inventory endpoint URL (used as the stored `url` value in the log)
VCARE_INVENTORY_URL = "https://www.vcareapi.com:8080/inventory"


def _extract_origin(request) -> str:
    """Return the calling origin from Origin or Referer header."""
    origin = request.META.get("HTTP_ORIGIN", "")
    if not origin:
        referer = request.META.get("HTTP_REFERER", "")
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

        if calling_origin:
            def _bare_host(url: str) -> str:
                from urllib.parse import urlparse
                host = urlparse(url).hostname or url
                return host.lower().removeprefix("www.")

            if _bare_host(calling_origin) != _bare_host(registered_origin):
                logger.warning(
                    "Origin mismatch for key %s: expected %s, got %s",
                    secret_key, registered_origin, calling_origin,
                )
                return JsonResponse({"error": "Origin not allowed."}, status=403)

        # ------------------------------------------------------------------ #
        # 5. Validate action + IMEI
        # ------------------------------------------------------------------ #
        SUPPORTED_ACTIONS = ("esim_check", "esim_update", "esim_v_check")
        if action not in SUPPORTED_ACTIONS:
            return JsonResponse(
                {"error": f"Unknown action '{action}'. Supported: {', '.join(SUPPORTED_ACTIONS)}"},
                status=400,
            )

        if not imei:
            return JsonResponse({"error": "Missing 'imei' field."}, status=400)

        imei = str(imei).strip()

        # ------------------------------------------------------------------ #
        # 6. esim_check — table lookup only, no VCare API call
        # ------------------------------------------------------------------ #
        if action == "esim_check":
            imei_exists = ESIMCheckerLog.objects.filter(imei=imei).exists()

            if imei_exists:
                logger.info("esim_check: IMEI %s found in table → compatible=true", imei)
                endpoint.increment_hits()
                return JsonResponse({
                    "success": True,
                    "imei": imei,
                    "esimCompatible": True,
                    "compatible": True,
                    "message": "Device is compatible.",
                })
            else:
                logger.info("esim_check: IMEI %s not found in table → compatible=false", imei)
                endpoint.increment_hits()
                return JsonResponse({
                    "success": True,
                    "imei": imei,
                    "esimCompatible": False,
                    "compatible": False,
                    "message": "Device is not compatible with our network.",
                })

        # ------------------------------------------------------------------ #
        # 7. esim_update — insert IMEI into table, no VCare API call
        # ------------------------------------------------------------------ #
        if action == "esim_update":
            try:
                cached = ESIMCheckerLog.objects.get(imei=imei)
                cached.increment_hit_count()
                logger.info("esim_update: IMEI %s already exists — incremented hit_count", imei)
                endpoint.increment_hits()
                return JsonResponse({
                    "success": True,
                    "imei": imei,
                    "esimCompatible": True,
                    "compatible": True,
                    "message": "eSIM record already exists — hit count updated.",
                })

            except ESIMCheckerLog.DoesNotExist:
                esim_payload = {
                    "data": {
                        "RESULT": {
                            "responseDetails": {
                                "inquireDeviceStatusResponse": {
                                    "deviceStatusDetails": {
                                        "attCompatibility": "GREEN",
                                    }
                                }
                            }
                        }
                    }
                }
                try:
                    ESIMCheckerLog.objects.create(
                        imei=imei,
                        url=VCARE_INVENTORY_URL,
                        hit_count=1,
                        cached_response=esim_payload,
                    )
                    logger.info("esim_update: IMEI %s inserted into ESIMCheckerLog", imei)
                except Exception as exc:
                    logger.error("esim_update: failed to insert IMEI %s: %s", imei, exc)
                    return JsonResponse(
                        {"error": "Failed to insert eSIM record. Please try again."},
                        status=500,
                    )

                endpoint.increment_hits()
                return JsonResponse({
                    "success": True,
                    "imei": imei,
                    "esimCompatible": True,
                    "compatible": True,
                    "message": "eSIM record inserted successfully.",
                })

        # ------------------------------------------------------------------ #
        # 8. esim_v_check — DB cache first; VCare API only on cache miss
        # ------------------------------------------------------------------ #
        if action == "esim_v_check":
            # Step 1: check ESIMCheckerLog table first
            try:
                cached = ESIMCheckerLog.objects.get(imei=imei)
                # Cache HIT — skip VCare API entirely, return cached response
                cached.increment_hit_count()
                logger.info("esim_v_check: IMEI %s found in ESIMCheckerLog (cache hit) — skipping VCare API", imei)
                endpoint.increment_hits()
                return JsonResponse({
                    "success": True,
                    "imei": imei,
                    "esimCompatible": True,
                    "compatible": True,
                    "source": "cache",
                    "message": "Device is compatible.",
                    "data": cached.cached_response,
                })
            except ESIMCheckerLog.DoesNotExist:
                pass  # Cache MISS — fall through to VCare API call

            # Step 2: cache miss — call VCare API
            logger.info("esim_v_check: IMEI %s not in ESIMCheckerLog — calling VCare API", imei)
            try:
                result = check_device_esim_compatibility(imei)
            except RuntimeError as exc:
                logger.error("esim_v_check: VCare API error for IMEI %s: %s", imei, exc)
                return JsonResponse(
                    {"error": "Upstream API error. Please try again later."},
                    status=502,
                )

            device_status = (
                result.get("data", {})
                .get("RESULT", {})
                .get("responseDetails", {})
                .get("inquireDeviceStatusResponse", {})
                .get("deviceStatusDetails", {})
            )
            is_green = device_status.get("attCompatibility") == "GREEN" if device_status else False

            if is_green:
                # GREEN → insert IMEI into ESIMCheckerLog table, then return full VCare response
                try:
                    ESIMCheckerLog.objects.create(
                        imei=imei,
                        url=VCARE_INVENTORY_URL,
                        hit_count=1,
                        cached_response=result,
                    )
                    logger.info("esim_v_check: IMEI %s is GREEN — inserted into ESIMCheckerLog", imei)
                except Exception as exc:
                    logger.error("esim_v_check: failed to insert IMEI %s: %s", imei, exc)

                endpoint.increment_hits()
                # Return the VCare response as-is, with compatible flags added
                return JsonResponse({
                    "success": True,
                    "imei": imei,
                    "esimCompatible": True,
                    "compatible": True,
                    "source": "vcare",
                    "message": "Device is compatible.",
                    "data": result,
                })
            else:
                logger.info("esim_v_check: IMEI %s → NOT GREEN (compatible=false)", imei)
                endpoint.increment_hits()
                return JsonResponse({
                    "success": True,
                    "imei": imei,
                    "esimCompatible": False,
                    "compatible": False,
                    "source": "vcare",
                    "message": "Device is not compatible with our network.",
                    "data": result,
                })

    def options(self, request, *args, **kwargs):
        """Handle CORS preflight."""
        response = JsonResponse({})
        _add_cors_headers(response, request)
        return response


def _add_cors_headers(response, request):
    origin = request.META.get("HTTP_ORIGIN", "")
    if origin:
        if ESIMCheckerEndpoint.objects.filter(
            site_url__icontains=origin.replace("https://", "").replace("http://", ""),
            is_active=True,
        ).exists():
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, X-Secret-Key"
            response["Access-Control-Max-Age"] = "86400"
    return response