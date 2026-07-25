from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.stores_master.models.godown_creation_master import GodownCreationMaster
from apps.stores_master.serializers.godown_creation_master_serializer import (
    GodownCreationMasterSerializer,
)
from apps.stores_master.permissions import IsAuthenticated


class GodownCreationMasterViewSet(ModelViewSet):
    """
    Godown Creation Master API
    -----------------------------
    CRUD operations for GodownCreationMaster.
    """

    queryset = GodownCreationMaster.objects.filter(is_deleted=False)
    serializer_class = GodownCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create godown",
        request_body=GodownCreationMasterSerializer,
        responses={201: GodownCreationMasterSerializer},
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
        operation_summary="Update godown",
        request_body=GodownCreationMasterSerializer,
        responses={200: GodownCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        godown = self.get_object()
        godown.is_deleted = True
        godown.is_active = False
        godown.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        godown.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
