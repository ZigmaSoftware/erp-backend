from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.item_group_creation_master import ItemGroupCreationMaster
from apps.sales_master.serializers.item_group_creation_master_serializer import (
    ItemGroupCreationMasterSerializer,
)


class ItemGroupCreationMasterViewSet(ModelViewSet):
    """
    Item Group Creation Master API
    ------------------------------
    CRUD operations for ItemGroupCreationMaster.
    """

    queryset = ItemGroupCreationMaster.objects.filter(is_deleted=False)
    serializer_class = ItemGroupCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create item group",
        request_body=ItemGroupCreationMasterSerializer,
        responses={201: ItemGroupCreationMasterSerializer},
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
        operation_summary="Update item group",
        request_body=ItemGroupCreationMasterSerializer,
        responses={200: ItemGroupCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        item_group = self.get_object()
        item_group.is_deleted = True
        item_group.is_active = False
        item_group.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        item_group.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
