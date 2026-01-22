from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.common_master.views.debug import DebugHeadersView
from apps.em_master.views.equipment_typemaster_viewset import EquipmentTypeMasterViewSet

router = DefaultRouter()

router.register(r"equipment-types", EquipmentTypeMasterViewSet, basename="equipment-type")

urlpatterns = router.urls + [
    path("debug/headers/", DebugHeadersView.as_view(), name="debug-headers"),
]
