from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.target_entry_master import TargetEntryMaster
from apps.sales_master.serializers.target_entry_master_serializer import (
    TargetEntryMasterSerializer,
)


class TargetEntryMasterViewSet(ModelViewSet):
    """
    Target Entry Master API
    ------------------------
    CRUD operations for TargetEntryMaster (header).
    """

    queryset = (
        TargetEntryMaster.objects.filter(is_deleted=False)
        .select_related("site_id")
        .prefetch_related("items")
    )
    serializer_class = TargetEntryMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create target entry",
        request_body=TargetEntryMasterSerializer,
        responses={201: TargetEntryMasterSerializer},
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
        operation_summary="Update target entry",
        request_body=TargetEntryMasterSerializer,
        responses={200: TargetEntryMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        target_entry = self.get_object()
        target_entry.is_deleted = True
        target_entry.is_active = False
        target_entry.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        target_entry.save(update_fields=["is_deleted", "is_active", "updated_by"])
        target_entry.items.filter(is_deleted=False).update(
            is_deleted=True, is_active=False
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
