from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.icw_supplier_creation import IcwSupplierCreation
from apps.sales_master.serializers.icw_supplier_creation_serializer import (
    IcwSupplierCreationSerializer,
)


class IcwSupplierCreationViewSet(ModelViewSet):
    """
    ICW Supplier Creation API
    -------------------------
    CRUD operations for ICW supplier creation.
    """

    queryset = (
        IcwSupplierCreation.objects.filter(is_deleted=False)
        .select_related("country_id", "state_id", "district_id", "city_id")
        .prefetch_related("sites")
    )
    serializer_class = IcwSupplierCreationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create ICW supplier",
        request_body=IcwSupplierCreationSerializer,
        responses={201: IcwSupplierCreationSerializer},
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
        operation_summary="Update ICW supplier",
        request_body=IcwSupplierCreationSerializer,
        responses={200: IcwSupplierCreationSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        supplier = self.get_object()
        supplier.is_deleted = True
        supplier.is_active = False
        supplier.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        supplier.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
