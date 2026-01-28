from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.common_master.views.debug import DebugHeadersView
from apps.em_master.views.equipment_typemaster_viewset import EquipmentTypeMasterViewSet
from apps.em_master.views.equipment_modelmaster_viewset import EquipmentModelMasterViewSet
from apps.em_master.views.contractormaster_viewset import ContractorMasterViewSet
from apps.em_master.views.vehicle_suppliermaster_viewset import VehicleSupplierMasterViewSet

router = DefaultRouter()

router.register(r"equipment-types", EquipmentTypeMasterViewSet, basename="equipment-type")
router.register(
    r"equipment-models", EquipmentModelMasterViewSet, basename="equipment-model"
)
router.register(
    r"contractor-models", ContractorMasterViewSet, basename="constractor-model"
)
router.register(
    r"vehicle-suppliers", VehicleSupplierMasterViewSet, basename="vehicle-supplier"
)

urlpatterns = router.urls + [
    path("debug/headers/", DebugHeadersView.as_view(), name="debug-headers"),
]
