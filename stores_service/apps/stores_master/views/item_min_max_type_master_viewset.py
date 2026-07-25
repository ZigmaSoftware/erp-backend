from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.stores_master.models.item_min_max_type_master import ItemMinMaxTypeMaster
from apps.stores_master.serializers.item_min_max_type_master_serializer import (
    ItemMinMaxTypeMasterSerializer,
)
from apps.stores_master.permissions import IsAuthenticated


class ItemMinMaxTypeMasterViewSet(ModelViewSet):
    """
    Item Min Max Type Master API
    ------------------------------
    CRUD operations for ItemMinMaxTypeMaster.
    """

    queryset = ItemMinMaxTypeMaster.objects.filter(is_deleted=False)
    serializer_class = ItemMinMaxTypeMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create item min max type",
        request_body=ItemMinMaxTypeMasterSerializer,
        responses={201: ItemMinMaxTypeMasterSerializer},
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
        operation_summary="Update item min max type",
        request_body=ItemMinMaxTypeMasterSerializer,
        responses={200: ItemMinMaxTypeMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        item_type = self.get_object()
        item_type.is_deleted = True
        item_type.is_active = False
        item_type.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        item_type.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
