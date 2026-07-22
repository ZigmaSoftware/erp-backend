from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.transport_entry_master import TransportEntryMaster
from apps.sales_master.serializers.transport_entry_master_serializer import (
    TransportEntryMasterSerializer,
)


class TransportEntryMasterViewSet(ModelViewSet):
    """
    Transport Entry Master API
    ---------------------------
    CRUD operations for TransportEntryMaster.
    """

    queryset = TransportEntryMaster.objects.filter(is_deleted=False)
    serializer_class = TransportEntryMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create transport entry",
        request_body=TransportEntryMasterSerializer,
        responses={201: TransportEntryMasterSerializer},
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
        operation_summary="Update transport entry",
        request_body=TransportEntryMasterSerializer,
        responses={200: TransportEntryMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        transport_entry = self.get_object()
        transport_entry.is_deleted = True
        transport_entry.is_active = False
        transport_entry.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        transport_entry.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
