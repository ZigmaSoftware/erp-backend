from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from django.db import transaction

from apps.common_master.models.site import Site
from apps.common_master.serializers.site import SiteSerializer


class SiteViewSet(ModelViewSet):
    """
    Site Master API
    ---------------
    CRUD operations for Site.
    """

    queryset = Site.objects.filter(is_deleted=False)
    serializer_class = SiteSerializer
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

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        site = self.get_object()
        username = (
            request.user.username
            if request.user.is_authenticated
            else None
        )

        # 1. Soft-delete related plants
        site.plants.filter(is_deleted=False).update(
            is_deleted=True,
            is_active=False,
            updated_by=username
        )

        # 2. Soft-delete site
        site.is_deleted = True
        site.is_active = False
        site.updated_by = username
        site.save(update_fields=["is_deleted", "is_active", "updated_by"])

        return Response(status=status.HTTP_204_NO_CONTENT)
