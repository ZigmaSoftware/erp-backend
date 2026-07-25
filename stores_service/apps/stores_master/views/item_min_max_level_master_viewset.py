from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.stores_master.models.item_min_max_level_master import ItemMinMaxLevelMaster
from apps.stores_master.serializers.item_min_max_level_master_serializer import (
    ItemMinMaxLevelMasterSerializer,
)
from apps.stores_master.permissions import IsAuthenticated


class ItemMinMaxLevelMasterViewSet(ModelViewSet):
    """
    Item Min Max Level Master API
    --------------------------------
    CRUD operations for ItemMinMaxLevelMaster.
    """

    queryset = ItemMinMaxLevelMaster.objects.filter(is_deleted=False).select_related("type")
    serializer_class = ItemMinMaxLevelMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create item min max level",
        request_body=ItemMinMaxLevelMasterSerializer,
        responses={201: ItemMinMaxLevelMasterSerializer},
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
        operation_summary="Update item min max level",
        request_body=ItemMinMaxLevelMasterSerializer,
        responses={200: ItemMinMaxLevelMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        level = self.get_object()
        level.is_deleted = True
        level.is_active = False
        level.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        level.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
