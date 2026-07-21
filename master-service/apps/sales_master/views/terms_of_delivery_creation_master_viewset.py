from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.terms_of_delivery_creation_master import (
    TermsOfDeliveryCreationMaster,
)
from apps.sales_master.serializers.terms_of_delivery_creation_master_serializer import (
    TermsOfDeliveryCreationMasterSerializer,
)


class TermsOfDeliveryCreationMasterViewSet(ModelViewSet):
    """
    Terms Of Delivery Creation Master API
    -------------------------------------
    CRUD operations for TermsOfDeliveryCreationMaster.
    """

    queryset = TermsOfDeliveryCreationMaster.objects.filter(is_deleted=False)
    serializer_class = TermsOfDeliveryCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create terms of delivery",
        request_body=TermsOfDeliveryCreationMasterSerializer,
        responses={201: TermsOfDeliveryCreationMasterSerializer},
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
        operation_summary="Update terms of delivery",
        request_body=TermsOfDeliveryCreationMasterSerializer,
        responses={200: TermsOfDeliveryCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        terms_of_delivery = self.get_object()
        terms_of_delivery.is_deleted = True
        terms_of_delivery.is_active = False
        terms_of_delivery.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        terms_of_delivery.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
