from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.stores_master.models.subgroup_creation_master import SubGroupCreationMaster
from apps.stores_master.serializers.subgroup_creation_master_serializer import (
    SubGroupCreationMasterSerializer,
)
from apps.stores_master.permissions import IsAuthenticated


class SubGroupCreationMasterViewSet(ModelViewSet):
    """
    Sub Group Creation Master API
    -------------------------------
    CRUD operations for SubGroupCreationMaster.
    """

    queryset = SubGroupCreationMaster.objects.filter(is_deleted=False).select_related("group")
    serializer_class = SubGroupCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create subgroup",
        request_body=SubGroupCreationMasterSerializer,
        responses={201: SubGroupCreationMasterSerializer},
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
        operation_summary="Update subgroup",
        request_body=SubGroupCreationMasterSerializer,
        responses={200: SubGroupCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        subgroup = self.get_object()
        subgroup.is_deleted = True
        subgroup.is_active = False
        subgroup.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        subgroup.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
