from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.em_master.models.machinery_hire import MachineryHire
from apps.em_master.serializers.machinery_hire_serializer import MachineryHireSerializer


class MachineryHireViewSet(ModelViewSet):
    """
    Machinery hire API.
    """

    queryset = MachineryHire.objects.filter(is_deleted=False)
    serializer_class = MachineryHireSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"

    def get_queryset(self):
        queryset = MachineryHire.objects.select_related(
            "vehicle_id",
            "site_id",
            "equipment_model_id",
            "equipment_type_id",
        )

        filters = {
            "site": self.request.query_params.get("site"),
            "vehicle": self.request.query_params.get("vehicle"),
            "equipment_type": self.request.query_params.get("equipment_type"),
            "equipment_model": self.request.query_params.get("equipment_model"),
        }

        for field, value in filters.items():
            if value:
                queryset = queryset.filter(**{f"{field}__unique_id": value})

        return queryset

    @swagger_auto_schema(
        operation_summary="Create machinery hire record",
        request_body=MachineryHireSerializer,
        responses={201: MachineryHireSerializer},
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

    @swagger_auto_schema(
        operation_summary="Update machinery hire record",
        request_body=MachineryHireSerializer,
        responses={200: MachineryHireSerializer},
    )
    def perform_update(self, serializer):
        username = (
            self.request.user.username
            if self.request.user.is_authenticated
            else None
        )
        serializer.save(updated_by=username)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = (
            request.user.username if request.user.is_authenticated else None
        )
        instance.is_deleted = True
        instance.is_active = False
        instance.updated_by = username
        instance.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
