from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common_master.models.state import State
from apps.common_master.serializers.state_serializer import StateSerializer


class StateViewSet(ModelViewSet):
    """
    State Master API
    ---------------
    CRUD operations for State.
    """

    queryset = State.objects.filter(is_deleted=False)
    serializer_class = StateSerializer
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
        state = self.get_object()
        state.is_deleted = True
        state.is_active = False
        state.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        state.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
