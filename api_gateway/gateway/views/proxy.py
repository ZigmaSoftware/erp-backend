import logging

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views import View

logger = logging.getLogger(__name__)


class ServiceProxyView(View):
    """
    Generic reverse proxy for a single backend microservice.

    Which service a route targets is set via `.as_view(service="...")`
    in urls.py, and its target base URL comes from
    `settings.SERVICE_URLS[service]` (see api_gateway/config/settings.py).

    To add a new backend service: add one entry to SERVICE_URLS and one
    `path()` line in gateway/urls.py using this same view - no new class.
    """

    service: str = ""
    # Auth service has no downstream notion of "current user" to forward.
    forward_user_context = True

    def dispatch(self, request, *args, **kwargs):
        base_url = settings.SERVICE_URLS.get(self.service)
        if not base_url:
            logger.error("No SERVICE_URLS entry configured for %r", self.service)
            return JsonResponse(
                {"detail": f"Service '{self.service}' is not configured"},
                status=500,
            )

        prefix = f"/api/{self.service}/"
        path = request.path[len(prefix):] if request.path.startswith(prefix) else request.path
        url = f"{base_url.rstrip('/')}/{path}"

        headers = {}

        content_type = request.headers.get("Content-Type")
        if content_type:
            headers["Content-Type"] = content_type

        auth_header = request.headers.get("Authorization")
        if auth_header:
            headers["Authorization"] = auth_header

        if self.forward_user_context:
            jwt_payload = getattr(request, "jwt_payload", None) or {}
            headers.update({
                "X-User-Id": str(jwt_payload.get("sub")),
                "X-Username": jwt_payload.get("username", ""),
                "X-Groups": ",".join(jwt_payload.get("groups", [])),
            })

        logger.debug("Proxy %s %s -> %s", request.method, request.path, url)

        try:
            response = requests.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.GET,
                data=request.body,
                timeout=settings.PROXY_TIMEOUT,
            )
        except requests.RequestException:
            logger.exception("%s unreachable", self.service)
            return JsonResponse({"detail": "Service unavailable"}, status=503)

        try:
            body = response.json()
            return JsonResponse(body, status=response.status_code, safe=False)
        except ValueError:
            return JsonResponse(
                {"detail": response.text},
                status=response.status_code,
            )
