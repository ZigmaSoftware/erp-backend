from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.document_type_master import DocumentTypeMaster
from apps.sales_master.serializers.document_type_master_serializer import (
    DocumentTypeMasterSerializer,
)


class DocumentTypeMasterViewSet(ModelViewSet):
    """
    Document Type Master API
    -------------------------
    CRUD operations for DocumentTypeMaster.
    """

    queryset = DocumentTypeMaster.objects.filter(is_deleted=False)
    serializer_class = DocumentTypeMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create document type",
        request_body=DocumentTypeMasterSerializer,
        responses={201: DocumentTypeMasterSerializer},
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
        operation_summary="Update document type",
        request_body=DocumentTypeMasterSerializer,
        responses={200: DocumentTypeMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        doc_type = self.get_object()
        doc_type.is_deleted = True
        doc_type.is_active = False
        doc_type.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        doc_type.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
