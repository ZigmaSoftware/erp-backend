from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.stores_master.models.group_creation_master import GroupCreationMaster
from apps.stores_master.serializers.group_creation_master_serializer import (
    GroupCreationMasterSerializer,
)
from apps.stores_master.permissions import IsAuthenticated


class GroupCreationMasterViewSet(ModelViewSet):
    """
    Group Creation Master API
    --------------------------
    CRUD operations for GroupCreationMaster.
    """

    queryset = GroupCreationMaster.objects.filter(is_deleted=False)
    serializer_class = GroupCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create group",
        request_body=GroupCreationMasterSerializer,
        responses={201: GroupCreationMasterSerializer},
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
        operation_summary="Update group",
        request_body=GroupCreationMasterSerializer,
        responses={200: GroupCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        group.is_deleted = True
        group.is_active = False
        group.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        group.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
