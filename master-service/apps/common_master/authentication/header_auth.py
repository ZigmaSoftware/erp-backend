from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication


class RemoteUser:
    def __init__(self, id=None, username=None, groups=None):
        self.id = int(id) if id is not None else None
        self.username = username
        self.groups = groups or []
        self.is_authenticated = True
        self.is_anonymous = False

    def __str__(self):
        return self.username or str(self.id)


class GatewayHeaderAuthentication(BaseAuthentication):
    """
    Authenticate requests asserted by an API gateway via headers.

    Looks for:
    - X-User-Id
    - X-Username
    - X-Groups
    """

    def authenticate(self, request):
        # VERY IMPORTANT: allow CORS preflight requests
        if request.method == "OPTIONS":
            return None

        x_user = request.META.get("HTTP_X_USER_ID")
        if not x_user:
            return None

        username = request.META.get("HTTP_X_USERNAME")
        groups_header = request.META.get("HTTP_X_GROUPS", "")
        groups = [g for g in groups_header.split(",") if g]

        User = get_user_model()

        try:
            user = User.objects.get(id=int(x_user))
            return (user, None)
        except User.DoesNotExist:
            # create lightweight authenticated principal
            return (
                RemoteUser(
                    id=x_user,
                    username=username,
                    groups=groups,
                ),
                None,
            )
