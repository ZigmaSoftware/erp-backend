from django.urls import path
from gateway.views.proxy import ServiceProxyView
from gateway.views.debug import DebugEchoView

# One line per backend microservice. `service` must match a key in
# settings.SERVICE_URLS. To add a new service, add its line here plus
# its entry in SERVICE_URLS - no new view class required.
urlpatterns = [
    path(
        "api/master-service/<path:path>",
        ServiceProxyView.as_view(service="master-service"),
    ),
    path(
        "api/auth-service/<path:path>",
        # Login/refresh bypass JWTAuthenticationMiddleware, so there is no
        # jwt_payload to forward as user-context headers for this service.
        ServiceProxyView.as_view(service="auth-service", forward_user_context=False),
    ),
    path(
        "api/sales-service/<path:path>",
        ServiceProxyView.as_view(service="sales-service"),
    ),
    path("api/debug/echo/", DebugEchoView.as_view()),
]
