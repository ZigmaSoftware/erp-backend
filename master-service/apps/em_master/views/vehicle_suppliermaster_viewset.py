from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.em_master.models.vehicle_suppliermaster import VehicleSupplierMaster
from apps.em_master.serializers.vehicle_suppliermaster_serializer import VehicleSupplierMasterSerializer


class VehicleSupplierMasterViewSet(ModelViewSet):
    """
    Vehicle Supplier Master API
    ---------------------------
    CRUD operations with image uploads.
    """

    queryset = VehicleSupplierMaster.objects.filter(is_deleted=False)
    serializer_class = VehicleSupplierMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create Vehicle Supplier",
        request_body=VehicleSupplierMasterSerializer,
        responses={201: VehicleSupplierMasterSerializer},
        consumes=["multipart/form-data"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    @swagger_auto_schema(
        operation_summary="Update Vehicle Supplier",
        request_body=VehicleSupplierMasterSerializer,
        responses={200: VehicleSupplierMasterSerializer},
        consumes=["multipart/form-data"],
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.is_active = False
        instance.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        instance.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
