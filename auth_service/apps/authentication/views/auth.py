from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.authentication.serializers.login import LoginSerializer
from apps.authentication.models.audit import AuthAuditLog
from apps.authentication.services.audit_utils import (
    get_client_ip,
    get_user_agent,
    parse_browser_os,
)
from erp_jwt.encoder import generate_access_token, generate_refresh_token
from erp_jwt.decoder import decode_token, JWTExpiredError, JWTInvalidError


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(username=username, password=password)

        ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        browser, os = parse_browser_os(user_agent)

        if not user:
            # 🔒 Log failed attempt
            AuthAuditLog.objects.create(
                user=None,
                event_type="LOGIN_FAILED",
                ip_address=ip,
                user_agent=user_agent,
                browser=browser,
                os=os,
                failure_reason="INVALID_CREDENTIALS",
                metadata={"username": username},
            )

            return Response(
                {"error": "INVALID_CREDENTIALS"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # ✅ Generate tokens
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        # ✅ Log success
        AuthAuditLog.objects.create(
            user=user,
            event_type="LOGIN_SUCCESS",
            ip_address=ip,
            user_agent=user_agent,
            browser=browser,
            os=os,
            metadata={"username": user.username},
        )

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": 3600,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "groups": list(user.groups.values_list("name", flat=True)),
                },
            },
            status=status.HTTP_200_OK,
        )


class LoginPageView(View):
    """Simple HTML login page (GET shows form, POST authenticates and sets session).

    Template: apps/authentication/templates/auth/login.html
    """

    def get(self, request):
        return render(request, "auth/login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        browser, os = parse_browser_os(user_agent)

        if not user:
            AuthAuditLog.objects.create(
                user=None,
                event_type="LOGIN_FAILED",
                ip_address=ip,
                user_agent=user_agent,
                browser=browser,
                os=os,
                failure_reason="INVALID_CREDENTIALS",
                metadata={"username": username},
            )
            return render(request, "auth/login.html", {"error": "Invalid credentials"}, status=401)

        # Log success and create session
        AuthAuditLog.objects.create(
            user=user,
            event_type="LOGIN_SUCCESS",
            ip_address=ip,
            user_agent=user_agent,
            browser=browser,
            os=os,
            metadata={"username": user.username},
        )

        auth_login(request, user)

        # Generate JWT tokens (same as API flow) and render them for the user
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        return render(
            request,
            "auth/login_success.html",
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": 3600,
                "user": user,
            },
        )


class TokenRefreshView(APIView):
    """Refresh an expired access token using a valid refresh token.
    
    Expected request:
    POST /api/auth/refresh/
    Content-Type: application/json
    
    {
        "refresh_token": "eyJhbGciOi..."
    }
    
    Response:
    {
        "access_token": "eyJhbGciOi...",
        "expires_in": 3600
    }
    """
    
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        refresh_token = request.data.get("refresh_token")
        
        if not refresh_token:
            return Response(
                {"error": "refresh_token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            # Decode and validate refresh token
            payload = decode_token(refresh_token, expected_type="refresh")
        except JWTExpiredError:
            return Response(
                {"error": "Refresh token expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except JWTInvalidError:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        # Extract user ID from token payload
        user_id = payload.get("sub")
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        # Generate new access token
        access_token = generate_access_token(user)
        
        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": 3600,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "groups": list(user.groups.values_list("name", flat=True)),
                },
            },
            status=status.HTTP_200_OK,
        )


    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        
        if not refresh_token:
            return Response(
                {"error": "refresh_token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            # Decode and validate refresh token
            payload = decode_token(refresh_token, expected_type="refresh")
        except JWTExpiredError:
            return Response(
                {"error": "Refresh token expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except JWTInvalidError:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        # Extract user ID from token payload
        user_id = payload.get("sub")
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        # Generate new access token
        access_token = generate_access_token(user)
        
        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": 3600,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "groups": list(user.groups.values_list("name", flat=True)),
                },
            },
            status=status.HTTP_200_OK,
        )
