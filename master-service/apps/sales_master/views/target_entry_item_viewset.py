from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.target_entry_item import TargetEntryItem
from apps.sales_master.serializers.target_entry_item_serializer import (
    TargetEntryItemSerializer,
)


class TargetEntryItemViewSet(ModelViewSet):
    """
    Target Entry Item API
    -----------------------
    CRUD operations for TargetEntryItem (sub-list line items).
    """

    serializer_class = TargetEntryItemSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = (
            TargetEntryItem.objects.filter(is_deleted=False)
            .select_related("target_entry", "item_type", "sub_category")
        )
        target_entry = self.request.query_params.get("target_entry")
        if target_entry:
            queryset = queryset.filter(target_entry__unique_id=target_entry)
        return queryset

    @swagger_auto_schema(
        operation_summary="Create target entry item",
        request_body=TargetEntryItemSerializer,
        responses={201: TargetEntryItemSerializer},
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
        operation_summary="Update target entry item",
        request_body=TargetEntryItemSerializer,
        responses={200: TargetEntryItemSerializer},
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
