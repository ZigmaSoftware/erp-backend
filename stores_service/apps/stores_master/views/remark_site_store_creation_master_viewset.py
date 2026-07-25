from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.stores_master.models.remark_site_store_creation_master import (
    RemarkSiteStoreCreationMaster,
)
from apps.stores_master.serializers.remark_site_store_creation_master_serializer import (
    RemarkSiteStoreCreationMasterSerializer,
)
from apps.stores_master.permissions import IsAuthenticated


class RemarkSiteStoreCreationMasterViewSet(ModelViewSet):
    """
    Remark Site Store Creation Master API
    ----------------------------------------
    CRUD operations for RemarkSiteStoreCreationMaster.
    """

    queryset = RemarkSiteStoreCreationMaster.objects.filter(is_deleted=False)
    serializer_class = RemarkSiteStoreCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create remark",
        request_body=RemarkSiteStoreCreationMasterSerializer,
        responses={201: RemarkSiteStoreCreationMasterSerializer},
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
        operation_summary="Update remark",
        request_body=RemarkSiteStoreCreationMasterSerializer,
        responses={200: RemarkSiteStoreCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        remark = self.get_object()
        remark.is_deleted = True
        remark.is_active = False
        remark.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        remark.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
