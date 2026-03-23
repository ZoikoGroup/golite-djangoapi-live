from corsheaders.signals import check_request_enabled
from django.dispatch import receiver

STATIC_ORIGINS = [
    "http://localhost:3000",
    "https://golitereact.vercel.app",
    "https://react.golitemobile.com",
    "https://lakhan-golite.vercel.app",
    "https://golitemobile.com",
    "https://www.golitemobile.com",
]

@receiver(check_request_enabled)
def cors_allow_origins(sender, request, **kwargs):
    try:
        origin = request.META.get("HTTP_ORIGIN", "")
        if not origin:
            return False

        # Check static origins
        if origin in STATIC_ORIGINS:
            return True

        # Check dynamic origins from database
        from apps.esim_checker.models import ESIMCheckerEndpoint
        return ESIMCheckerEndpoint.objects.filter(
            site_url=origin,
            is_active=True
        ).exists()

    except Exception:
        return False