from django.http import JsonResponse
from erp_jwt.decoder import decode_token, JWTExpiredError, JWTInvalidError


EXACT_EXCLUDED_PATHS = {
    "/api/auth/login/",
    "/api/auth/refresh/",
}

# Allow unauthenticated access to master-service API docs through the gateway.
PREFIX_EXCLUDED_PATHS = (
    "/api/master/api/docs/",
)


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip auth for excluded paths
        if request.path in EXACT_EXCLUDED_PATHS or request.path.startswith(PREFIX_EXCLUDED_PATHS):
            return self.get_response(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse(
                {"detail": "Authorization header missing"},
                status=401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = decode_token(token, expected_type="access")
        except JWTExpiredError:
            return JsonResponse({"detail": "Token expired"}, status=401)
        except JWTInvalidError:
            return JsonResponse({"detail": "Invalid token"}, status=401)

        # Attach user context to request
        request.jwt_payload = payload

        return self.get_response(request)
