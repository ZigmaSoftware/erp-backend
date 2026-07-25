from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.stores_master.models.unit_creation_master import UnitCreationMaster
from apps.stores_master.serializers.unit_creation_master_serializer import (
    UnitCreationMasterSerializer,
)
from apps.stores_master.permissions import IsAuthenticated


class UnitCreationMasterViewSet(ModelViewSet):
    """
    Unit Creation Master API
    -------------------------
    CRUD operations for UnitCreationMaster.
    """

    queryset = UnitCreationMaster.objects.filter(is_deleted=False)
    serializer_class = UnitCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create unit",
        request_body=UnitCreationMasterSerializer,
        responses={201: UnitCreationMasterSerializer},
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
        operation_summary="Update unit",
        request_body=UnitCreationMasterSerializer,
        responses={200: UnitCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        unit = self.get_object()
        unit.is_deleted = True
        unit.is_active = False
        unit.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        unit.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
