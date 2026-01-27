import requests
import logging
from django.http import JsonResponse
from django.views import View

logger = logging.getLogger(__name__)
MASTER_SERVICE_BASE = "http://127.0.0.1:8002"
AUTH_SERVICE_BASE = "http://127.0.0.1:8001"


class MasterServiceProxy(View):
    def dispatch(self, request, *args, **kwargs):
        path = request.path.replace("/api/master/", "")
        url = f"{MASTER_SERVICE_BASE}/{path}"

        headers = {}

        # Forward content type
        content_type = request.headers.get("Content-Type")
        if content_type:
            headers["Content-Type"] = content_type

        # Forward Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header:
            headers["Authorization"] = auth_header

        # User context headers
        headers.update({
            "X-User-Id": str(request.jwt_payload.get("sub")),
            "X-Username": request.jwt_payload.get("username", ""),
            "X-Groups": ",".join(request.jwt_payload.get("groups", [])),
        })

        logger.debug("Proxy %s %s -> %s", request.method, request.path, url)

        try:
            response = requests.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.GET,
                data=request.body,
                timeout=10,
            )
        except requests.RequestException:
            logger.exception("Master service unreachable")
            return JsonResponse({"detail": "Service unavailable"}, status=503)

        try:
            body = response.json()
            return JsonResponse(body, status=response.status_code, safe=False)
        except ValueError:
            return JsonResponse(
                {"detail": response.text},
                status=response.status_code,
            )


class AuthServiceProxy(View):
    def dispatch(self, request, *args, **kwargs):
        path = request.path.replace("/api/auth/", "")
        url = f"{AUTH_SERVICE_BASE}/{path}"

        headers = {}

        # Forward content type
        content_type = request.headers.get("Content-Type")
        if content_type:
            headers["Content-Type"] = content_type

        # Forward Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header:
            headers["Authorization"] = auth_header

        logger.debug("Proxy %s %s -> %s", request.method, request.path, url)

        try:
            response = requests.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.GET,
                data=request.body,
                timeout=10,
            )
        except requests.RequestException:
            logger.exception("Auth service unreachable")
            return JsonResponse({"detail": "Service unavailable"}, status=503)

        try:
            body = response.json()
            return JsonResponse(body, status=response.status_code, safe=False)
        except ValueError:
            return JsonResponse(
                {"detail": response.text},
                status=response.status_code,
            )

    