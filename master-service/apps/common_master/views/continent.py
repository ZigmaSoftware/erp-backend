from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common_master.models.continent import Continent
from apps.common_master.serializers.continent_serializer import ContinentSerializer


class ContinentViewSet(ModelViewSet):
    """
    Continent Master API
    --------------------
    CRUD operations for Continent.
    """

    queryset = Continent.objects.filter(is_deleted=False)
    serializer_class = ContinentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )
        if serializer.instance:
            serializer.instance.refresh_from_db()

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        continent = self.get_object()
        continent.is_deleted = True
        continent.is_active = False
        continent.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        continent.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
