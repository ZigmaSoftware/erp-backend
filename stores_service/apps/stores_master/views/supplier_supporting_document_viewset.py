from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.stores_master.models.supplier_supporting_document import (
    SupplierSupportingDocument,
)
from apps.stores_master.serializers.supplier_supporting_document_serializer import (
    SupplierSupportingDocumentSerializer,
)
from apps.stores_master.permissions import IsAuthenticated


class SupplierSupportingDocumentViewSet(ModelViewSet):
    """
    Supplier Supporting Document API
    -----------------------------------
    Upload/list/delete supporting documents attached to a SupplierCreationMaster.

    Deletion is a real hard delete (file is removed from storage too) --
    these are attachments, not master data, matching the legacy
    file_upload_db.php?action=del_file_upld behavior.
    """

    serializer_class = SupplierSupportingDocumentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = SupplierSupportingDocument.objects.select_related("supplier")
        supplier_id = self.request.query_params.get("supplier")
        if supplier_id:
            queryset = queryset.filter(supplier__unique_id=supplier_id)
        return queryset

    @swagger_auto_schema(
        operation_summary="Upload supplier supporting document",
        request_body=SupplierSupportingDocumentSerializer,
        responses={201: SupplierSupportingDocumentSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )
