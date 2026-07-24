from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.sales_shared.views import ApprovalHistoryViewSet

router = DefaultRouter()
router.register(r"approval-history", ApprovalHistoryViewSet, basename="approval-history")

urlpatterns = [
    path("", include(router.urls)),
]
