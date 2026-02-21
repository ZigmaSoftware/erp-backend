from django.db import transaction

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from drf_yasg.utils import swagger_auto_schema

from apps.em_master.models.vehicle_request import VehicleRequest, RequestStatus
from apps.em_master.serializers.vehicle_request_item_serializer import (
    VehicleRequestReadSerializer,
    VehicleRequestSerializer,
)


class VehicleRequestViewSet(ModelViewSet):
    """
    Vehicle request API.
    """

    queryset = VehicleRequest.objects.filter(is_deleted=False)
    serializer_class = VehicleRequestSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return VehicleRequestReadSerializer
        return VehicleRequestSerializer

    @swagger_auto_schema(
        operation_summary="Create vehicle request",
        request_body=VehicleRequestSerializer,
        responses={201: VehicleRequestSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    @swagger_auto_schema(
        operation_summary="Update vehicle request",
        request_body=VehicleRequestSerializer,
        responses={200: VehicleRequestSerializer},
    )
    @transaction.atomic
    def perform_update(self, serializer):
        instance = self.get_object()

        if instance.request_status == RequestStatus.APPROVED:
            raise serializers.ValidationError(
                "Approved requests cannot be modified."
            )

        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete the request so the audit trail remains.
        """
        instance = self.get_object()
        instance.updated_by = (
            request.user.username if request.user.is_authenticated else None
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
