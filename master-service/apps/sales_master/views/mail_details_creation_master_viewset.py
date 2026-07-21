from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.mail_details_creation_master import (
    MailDetailsCreationMaster,
)
from apps.sales_master.serializers.mail_details_creation_master_serializer import (
    MailDetailsCreationMasterSerializer,
)


class MailDetailsCreationMasterViewSet(ModelViewSet):
    """
    Mail Details Creation Master API
    --------------------------------
    CRUD operations for MailDetailsCreationMaster.
    """

    queryset = MailDetailsCreationMaster.objects.filter(is_deleted=False)
    serializer_class = MailDetailsCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create mail details",
        request_body=MailDetailsCreationMasterSerializer,
        responses={201: MailDetailsCreationMasterSerializer},
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
        operation_summary="Update mail details",
        request_body=MailDetailsCreationMasterSerializer,
        responses={200: MailDetailsCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        mail_details = self.get_object()
        mail_details.is_deleted = True
        mail_details.is_active = False
        mail_details.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        mail_details.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
