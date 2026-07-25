from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.stores_master.models.main_task_creation_master import MainTaskCreationMaster
from apps.stores_master.serializers.main_task_creation_master_serializer import (
    MainTaskCreationMasterSerializer,
)
from apps.stores_master.permissions import IsAuthenticated


class MainTaskCreationMasterViewSet(ModelViewSet):
    """
    Main Task Creation Master API
    -------------------------------
    CRUD operations for MainTaskCreationMaster.
    """

    queryset = MainTaskCreationMaster.objects.filter(is_deleted=False)
    serializer_class = MainTaskCreationMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create main task",
        request_body=MainTaskCreationMasterSerializer,
        responses={201: MainTaskCreationMasterSerializer},
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
        operation_summary="Update main task",
        request_body=MainTaskCreationMasterSerializer,
        responses={200: MainTaskCreationMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        main_task = self.get_object()
        main_task.is_deleted = True
        main_task.is_active = False
        main_task.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        main_task.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
