from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common_master.models.district import District
from apps.common_master.serializers.district_serializer import DistrictSerializer


class DistrictViewSet(ModelViewSet):
    """
    District Master API
    -------------------
    CRUD operations for District.
    """

    queryset = District.objects.filter(is_deleted=False)
    serializer_class = DistrictSerializer
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
        district = self.get_object()
        district.is_deleted = True
        district.is_active = False
        district.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        district.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
