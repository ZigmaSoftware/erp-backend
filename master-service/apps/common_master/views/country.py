from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common_master.models.country import Country
from apps.common_master.serializers.country_serializer import CountrySerializer


class CountryViewSet(ModelViewSet):
    """
    Country Master API
    ------------------
    CRUD operations for Country.
    """

    queryset = Country.objects.filter(is_deleted=False)
    serializer_class = CountrySerializer
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
        country = self.get_object()
        country.is_deleted = True
        country.is_active = False
        country.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        country.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
