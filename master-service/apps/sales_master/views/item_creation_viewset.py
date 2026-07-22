from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.item_creation import ItemCreation
from apps.sales_master.serializers.item_creation_serializer import (
    ItemCreationSerializer,
)


class ItemCreationViewSet(ModelViewSet):
    """
    Item Creation API
    -----------------
    CRUD operations for ItemCreation.
    """

    queryset = (
        ItemCreation.objects.filter(is_deleted=False)
        .select_related("item_type_id", "category_id", "site_id")
    )
    serializer_class = ItemCreationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create item",
        request_body=ItemCreationSerializer,
        responses={201: ItemCreationSerializer},
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
        operation_summary="Update item",
        request_body=ItemCreationSerializer,
        responses={200: ItemCreationSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        item.is_deleted = True
        item.is_active = False
        item.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        item.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
