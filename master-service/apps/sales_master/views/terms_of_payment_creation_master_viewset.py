from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.terms_of_payment_creation_master import (
    TermsOfPaymentCreationMaster,
)
from apps.sales_master.serializers.terms_of_payment_creation_master_serializer import (
    TermsOfPaymentCreationMasterSerializer,
)


class TermsOfPaymentCreationMasterViewSet(ModelViewSet):
    """
    Terms Of Payment Creation Master API
    ------------------------------------
    CRUD operations for TermsOfPaymentCreationMaster.
    """

    queryset = TermsOfPaymentCreationMaster.objects.filter(is_deleted=False)
    serializer_class = TermsOfPaymentCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create terms of payment",
        request_body=TermsOfPaymentCreationMasterSerializer,
        responses={201: TermsOfPaymentCreationMasterSerializer},
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
        operation_summary="Update terms of payment",
        request_body=TermsOfPaymentCreationMasterSerializer,
        responses={200: TermsOfPaymentCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        terms_of_payment = self.get_object()
        terms_of_payment.is_deleted = True
        terms_of_payment.is_active = False
        terms_of_payment.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        terms_of_payment.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
