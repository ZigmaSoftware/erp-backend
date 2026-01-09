from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common_master.models.city import City
from apps.common_master.serializers.city_serializer import CitySerializer


class CityViewSet(ModelViewSet):
    """
    City Master API
    --------------
    CRUD operations for City.
    """

    queryset = City.objects.filter(is_deleted=False)
    serializer_class = CitySerializer
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
        city = self.get_object()
        city.is_deleted = True
        city.is_active = False
        city.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        city.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
