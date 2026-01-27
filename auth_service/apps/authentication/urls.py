from django.urls import path
from apps.authentication.views.auth import LoginView, LoginPageView, TokenRefreshView

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    # HTML login page at /api/auth/login_page/
    path("login_page/", LoginPageView.as_view(), name="auth-login-page"),
    # Token refresh endpoint
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
