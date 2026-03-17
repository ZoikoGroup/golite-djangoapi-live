"""
Middleware that injects CORS headers for registered, active endpoints.
Add to MIDDLEWARE in settings.py BEFORE CommonMiddleware.
"""
from .models import ESIMCheckerEndpoint
from django.http import HttpResponse
class ESIMCheckerCORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle preflight OPTIONS request immediately
        if request.method == "OPTIONS":
            response = HttpResponse()
            self._add_cors_headers(response, request)
            return response

        response = self.get_response(request)
        self._add_cors_headers(response, request)
        return response

    def _add_cors_headers(self, response, request):
        origin = request.META.get("HTTP_ORIGIN", "")
        if origin:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = "POST, OPTIONS, GET"
            response["Access-Control-Allow-Headers"] = "Content-Type, X-Secret-Key, Authorization"
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Max-Age"] = "86400"
        return response