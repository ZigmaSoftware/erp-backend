from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.em_master.models.equipment_typemaster import EquipmentTypeMaster
from apps.em_master.serializers.equipment_typemaster_serializer import EquipmentTypeMasterSerializer


class EquipmentTypeMasterViewSet(ModelViewSet):
    """
    Equipment Type Master API
    -------------------------
    CRUD operations for EquipmentTypeMaster with image uploads.
    """

    queryset = EquipmentTypeMaster.objects.filter(is_deleted=False)
    serializer_class = EquipmentTypeMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create equipment type",
        request_body=EquipmentTypeMasterSerializer,
        responses={201: EquipmentTypeMasterSerializer},
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
        if serializer.instance:
            serializer.instance.refresh_from_db()

    @swagger_auto_schema(
        operation_summary="Update equipment type",
        request_body=EquipmentTypeMasterSerializer,
        responses={200: EquipmentTypeMasterSerializer},
        consumes=["multipart/form-data"],
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        equipment_type = self.get_object()
        equipment_type.is_deleted = True
        equipment_type.is_active = False
        equipment_type.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        equipment_type.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
