from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.transport_medium_creation_master import (
    TransportMediumCreationMaster,
)
from apps.sales_master.serializers.transport_medium_creation_master_serializer import (
    TransportMediumCreationMasterSerializer,
)


class TransportMediumCreationMasterViewSet(ModelViewSet):
    """
    Transport Medium Creation Master API
    ------------------------------------
    CRUD operations for TransportMediumCreationMaster.
    """

    queryset = TransportMediumCreationMaster.objects.filter(is_deleted=False)
    serializer_class = TransportMediumCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create transport medium",
        request_body=TransportMediumCreationMasterSerializer,
        responses={201: TransportMediumCreationMasterSerializer},
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
        operation_summary="Update transport medium",
        request_body=TransportMediumCreationMasterSerializer,
        responses={200: TransportMediumCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        transport_medium = self.get_object()
        transport_medium.is_deleted = True
        transport_medium.is_active = False
        transport_medium.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        transport_medium.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
