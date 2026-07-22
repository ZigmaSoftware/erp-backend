from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.customer_item_purpose import CustomerItemPurpose
from apps.sales_master.serializers.customer_item_purpose_serializer import (
    CustomerItemPurposeSerializer,
)


class CustomerItemPurposeViewSet(ModelViewSet):
    """
    Customer Item / Purpose API
    -----------------------------
    CRUD operations for CustomerItemPurpose (sub-list line items).
    """

    serializer_class = CustomerItemPurposeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = (
            CustomerItemPurpose.objects.filter(is_deleted=False)
            .select_related("customer", "site", "item")
        )
        customer = self.request.query_params.get("customer")
        if customer:
            queryset = queryset.filter(customer__unique_id=customer)
        return queryset

    @swagger_auto_schema(
        operation_summary="Create customer item/purpose",
        request_body=CustomerItemPurposeSerializer,
        responses={201: CustomerItemPurposeSerializer},
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
        operation_summary="Update customer item/purpose",
        request_body=CustomerItemPurposeSerializer,
        responses={200: CustomerItemPurposeSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        item_purpose = self.get_object()
        item_purpose.is_deleted = True
        item_purpose.is_active = False
        item_purpose.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        item_purpose.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
