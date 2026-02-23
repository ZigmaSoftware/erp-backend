from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.em_master.models.vehicle_creation import VehicleCreation
from apps.em_master.serializers.vehicle_creation_serializer import (
    VehicleCreationSerializer,
)


class VehicleCreationViewSet(ModelViewSet):
    """
    Vehicle Creation API
    """

    queryset = (
        VehicleCreation.objects.filter(is_deleted=False)
        .select_related(
            "contractor",
            "supplier",
            "request",
            "site",
            "equipment_type",
            "equipment_model",
        )
    )

    serializer_class = VehicleCreationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"

    # ----------------------------
    # CREATE
    # ----------------------------
    @swagger_auto_schema(
        operation_summary="Create vehicle record",
        request_body=VehicleCreationSerializer,
        responses={201: VehicleCreationSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        username = (
            self.request.user.username
            if self.request.user.is_authenticated
            else None
        )
        serializer.save(created_by=username, updated_by=username)

    # ----------------------------
    # UPDATE
    # ----------------------------
    @swagger_auto_schema(
        operation_summary="Update vehicle record",
        request_body=VehicleCreationSerializer,
        responses={200: VehicleCreationSerializer},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        username = (
            self.request.user.username
            if self.request.user.is_authenticated
            else None
        )
        serializer.save(updated_by=username)

    # ----------------------------
    # SOFT DELETE
    # ----------------------------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        username = (
            request.user.username
            if request.user.is_authenticated
            else None
        )

        instance.is_deleted = True
        instance.is_active = False
        instance.updated_by = username
        instance.save(update_fields=["is_deleted", "is_active", "updated_by"])

        return Response(status=status.HTTP_204_NO_CONTENT)