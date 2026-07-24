from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.customer_creation_master import CustomerCreationMaster
from apps.sales_master.serializers.customer_creation_master_serializer import (
    CustomerCreationMasterSerializer,
)


class CustomerCreationMasterViewSet(ModelViewSet):
    """
    Customer Creation Master API
    ------------------------------
    CRUD operations for CustomerCreationMaster.
    """

    queryset = (
        CustomerCreationMaster.objects.filter(is_deleted=False)
        .prefetch_related("destinations", "item_purposes")
    )
    serializer_class = CustomerCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create customer",
        request_body=CustomerCreationMasterSerializer,
        responses={201: CustomerCreationMasterSerializer},
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
        operation_summary="Update customer",
        request_body=CustomerCreationMasterSerializer,
        responses={200: CustomerCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()
        customer.is_deleted = True
        customer.is_active = False
        customer.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        customer.save(update_fields=["is_deleted", "is_active", "updated_by"])
        customer.destinations.filter(is_deleted=False).update(
            is_deleted=True, is_active=False
        )
        customer.item_purposes.filter(is_deleted=False).update(
            is_deleted=True, is_active=False
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
