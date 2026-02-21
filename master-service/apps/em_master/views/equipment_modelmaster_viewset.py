from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from drf_yasg.utils import swagger_auto_schema

from apps.em_master.models.equipment_modelmaster import EquipmentModelMaster
from apps.em_master.serializers.equipment_modelmaster_serializer import (
    EquipmentModelMasterSerializer,
)


class EquipmentModelMasterViewSet(ModelViewSet):
    """
    Equipment Model Master API
    --------------------------
    CRUD operations with soft delete
    """

    queryset = EquipmentModelMaster.objects.filter(is_deleted=False)
    serializer_class = EquipmentModelMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create equipment model",
        request_body=EquipmentModelMasterSerializer,
        responses={201: EquipmentModelMasterSerializer},
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
        operation_summary="Update equipment model",
        request_body=EquipmentModelMasterSerializer,
        responses={200: EquipmentModelMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete
        """
        instance = self.get_object()
        instance.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
