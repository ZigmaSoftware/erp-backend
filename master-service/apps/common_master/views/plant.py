from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.common_master.models.plant import Plant
from apps.common_master.serializers.plant import PlantSerializer


class PlantViewSet(ModelViewSet):
    """
    Plant Master API
    ----------------
    CRUD operations for Plant.
    """

    queryset = Plant.objects.filter(is_deleted=False)
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        plant = self.get_object()
        plant.is_deleted = True
        plant.is_active = False
        plant.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        plant.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
