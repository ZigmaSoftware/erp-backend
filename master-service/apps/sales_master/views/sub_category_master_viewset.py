from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.sub_category_master import SubCategoryMaster
from apps.sales_master.serializers.sub_category_master_serializer import (
    SubCategoryMasterSerializer,
)


class SubCategoryMasterViewSet(ModelViewSet):
    """
    Sub Category Master API
    ------------------------
    CRUD operations for SubCategoryMaster.
    """

    queryset = SubCategoryMaster.objects.filter(is_deleted=False).select_related("item_type")
    serializer_class = SubCategoryMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create sub category",
        request_body=SubCategoryMasterSerializer,
        responses={201: SubCategoryMasterSerializer},
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
        operation_summary="Update sub category",
        request_body=SubCategoryMasterSerializer,
        responses={200: SubCategoryMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        sub_category = self.get_object()
        sub_category.is_deleted = True
        sub_category.is_active = False
        sub_category.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        sub_category.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
