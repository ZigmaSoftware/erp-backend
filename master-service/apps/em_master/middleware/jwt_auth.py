from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """Trust authentication asserted by an upstream API gateway.

    This middleware does NOT validate JWTs locally — the **gateway is responsible
    for validating tokens** and for forwarding authenticated user context via
    `X-User-Id`, `X-Username`, and `X-Groups` headers. When present, those
    headers are trusted and used to set `request.user`. If headers are missing,
    the normal Django authentication stack remains in effect.
    """

    def process_request(self, request):
        User = get_user_model()

        # Trust the gateway's forwarded user context first (recommended)
        x_user = request.META.get("HTTP_X_USER_ID")
        if x_user:
            username = request.META.get("HTTP_X_USERNAME")
            groups_header = request.META.get("HTTP_X_GROUPS", "")
            groups = [g for g in groups_header.split(",") if g]
            try:
                user = User.objects.get(id=int(x_user))
                request.user = user
                logger.debug("Loaded local user for X-User-Id=%s", x_user)
            except Exception:
                # Create a lightweight remote user object that signifies an
                # authenticated principal asserted by the gateway. This allows
                # `IsAuthenticated` and similar checks to pass without requiring
                # a local user record.
                class RemoteUser:
                    def __init__(self, id=None, username=None, groups=None):
                        self.id = int(id) if id is not None else None
                        self.username = username
                        self.groups = groups or []
                        self.is_authenticated = True
                        self.is_anonymous = False

                    def __str__(self):
                        return self.username or str(self.id)

                request.user = RemoteUser(id=x_user, username=username, groups=groups)
                logger.debug("Created RemoteUser for X-User-Id=%s (username=%s)", x_user, username)
            return

        # No gateway header found — do not perform JWT validation here.
        # Leave Django's authentication (session/auth middleware) to populate
        # request.user if available.
        request.user = getattr(request, "user", AnonymousUser())

