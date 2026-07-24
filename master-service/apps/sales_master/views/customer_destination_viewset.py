from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.customer_destination import CustomerDestination
from apps.sales_master.serializers.customer_destination_serializer import (
    CustomerDestinationSerializer,
)


class CustomerDestinationViewSet(ModelViewSet):
    """
    Customer Destination API
    --------------------------
    CRUD operations for CustomerDestination (sub-list line items).
    """

    serializer_class = CustomerDestinationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = (
            CustomerDestination.objects.filter(is_deleted=False)
            .select_related("customer", "site")
        )
        customer = self.request.query_params.get("customer")
        if customer:
            queryset = queryset.filter(customer__unique_id=customer)
        return queryset

    @swagger_auto_schema(
        operation_summary="Create customer destination",
        request_body=CustomerDestinationSerializer,
        responses={201: CustomerDestinationSerializer},
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
        operation_summary="Update customer destination",
        request_body=CustomerDestinationSerializer,
        responses={200: CustomerDestinationSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        destination = self.get_object()
        destination.is_deleted = True
        destination.is_active = False
        destination.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        destination.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
