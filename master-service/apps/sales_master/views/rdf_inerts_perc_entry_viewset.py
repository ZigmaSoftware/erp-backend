from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.rdf_inerts_perc_entry import RdfInertsPercEntry
from apps.sales_master.serializers.rdf_inerts_perc_entry_serializer import (
    RdfInertsPercEntrySerializer,
)


class RdfInertsPercEntryViewSet(ModelViewSet):
    """
    RDF & Inerts Percentage Entry API
    ---------------------------------
    CRUD operations for RDF & Inerts percentage entries.
    """

    queryset = RdfInertsPercEntry.objects.filter(is_deleted=False)
    serializer_class = RdfInertsPercEntrySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create RDF & Inerts percentage entry",
        request_body=RdfInertsPercEntrySerializer,
        responses={201: RdfInertsPercEntrySerializer},
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
        operation_summary="Update RDF & Inerts percentage entry",
        request_body=RdfInertsPercEntrySerializer,
        responses={200: RdfInertsPercEntrySerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        entry = self.get_object()
        entry.is_deleted = True
        entry.is_active = False
        entry.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        entry.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
