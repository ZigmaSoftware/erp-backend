from django.http import JsonResponse
from django.views import View


class DebugHeadersView(View):
    """Return incoming headers and basic request.user info for debugging gateway->master."""

    def get(self, request):
        headers = {k: v for k, v in request.headers.items()}
        user = getattr(request, 'user', None)
        user_info = None
        try:
            user_info = {
                'type': type(user).__name__ if user is not None else None,
                'is_authenticated': bool(getattr(user, 'is_authenticated', False)),
                'id': getattr(user, 'id', None),
                'username': getattr(user, 'username', None),
            }
        except Exception as exc:
            user_info = {'error': str(exc)}

        return JsonResponse({'headers': headers, 'user': user_info})
