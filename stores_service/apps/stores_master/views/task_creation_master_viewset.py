from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.stores_master.models.task_creation_master import TaskCreationMaster
from apps.stores_master.serializers.task_creation_master_serializer import (
    TaskCreationMasterSerializer,
)
from apps.stores_master.permissions import IsAuthenticated


class TaskCreationMasterViewSet(ModelViewSet):
    """
    Task Creation Master API
    --------------------------
    CRUD operations for TaskCreationMaster.
    """

    queryset = TaskCreationMaster.objects.filter(is_deleted=False)
    serializer_class = TaskCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create task",
        request_body=TaskCreationMasterSerializer,
        responses={201: TaskCreationMasterSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )
        if serializer.instance:
            serializer.instance.refresh_from_db()

    @swagger_auto_schema(
        operation_summary="Update task",
        request_body=TaskCreationMasterSerializer,
        responses={200: TaskCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        task.is_deleted = True
        task.is_active = False
        task.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        task.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
