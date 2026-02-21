from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.em_master.models.contractormaster import ContractorMaster
from apps.em_master.serializers.contractormaster_serializer import (
    ContractorMasterSerializer,
)


class ContractorMasterViewSet(ModelViewSet):
    """
    Contractor Master API
    ---------------------
    CRUD operations for ContractorMaster
    """

    queryset = ContractorMaster.objects.filter(is_deleted=False)
    serializer_class = ContractorMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    @swagger_auto_schema(
        operation_summary="Create contractor",
        request_body=ContractorMasterSerializer,
        responses={201: ContractorMasterSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username
            if self.request.user.is_authenticated
            else None,
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None,
            is_active=True,
            is_deleted=False,
        )
        if serializer.instance:
            serializer.instance.refresh_from_db()

    @swagger_auto_schema(
        operation_summary="Update contractor",
        request_body=ContractorMasterSerializer,
        responses={200: ContractorMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def get_queryset(self):
        """
        Optional filters:
        ?is_active=true/false
        """
        queryset = super().get_queryset()
        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        return queryset

    def destroy(self, request, *args, **kwargs):
        contractor = self.get_object()
        contractor.is_deleted = True
        contractor.is_active = False
        contractor.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        contractor.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
