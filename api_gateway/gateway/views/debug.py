from django.http import JsonResponse
from django.views import View
import logging

logger = logging.getLogger(__name__)


class DebugEchoView(View):
    def get(self, request):
        # Log the incoming request headers and origin for debugging CORS
        logger.debug("DebugEcho received GET from origin=%s headers=%s", request.headers.get('Origin'), dict(request.headers))

        # Return a subset of headers for inspection
        headers = {k: v for k, v in request.headers.items()}
        return JsonResponse({"method": "GET", "headers": headers, "origin": request.headers.get("Origin")})

    def options(self, request):
        # Log preflight
        logger.debug("DebugEcho received OPTIONS preflight from origin=%s headers=%s", request.headers.get('Origin'), dict(request.headers))
        # Let CORS preflight succeed: django-cors-headers will add headers.
        return JsonResponse({"status": "ok"})
