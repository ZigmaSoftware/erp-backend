from django.urls import path
from apps.authentication.views.auth import LoginView, LoginPageView

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    # HTML login page at /api/auth/login_page/
    path("login_page/", LoginPageView.as_view(), name="auth-login-page"),
]
