"""
URL configuration for API Gateway.
"""

from django.urls import path, include

urlpatterns = [
    path("", include("gateway.urls")),
]