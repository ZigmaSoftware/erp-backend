from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.scrap_sales_category_master import ScrapSalesCategoryMaster
from apps.sales_master.serializers.scrap_sales_category_master_serializer import (
    ScrapSalesCategoryMasterSerializer,
)


class ScrapSalesCategoryMasterViewSet(ModelViewSet):
    """
    Scrap Sales Category Master API
    --------------------------------
    CRUD operations for ScrapSalesCategoryMaster.
    """

    queryset = ScrapSalesCategoryMaster.objects.filter(is_deleted=False)
    serializer_class = ScrapSalesCategoryMasterSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="Create scrap sales category",
        request_body=ScrapSalesCategoryMasterSerializer,
        responses={201: ScrapSalesCategoryMasterSerializer},
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
        operation_summary="Update scrap sales category",
        request_body=ScrapSalesCategoryMasterSerializer,
        responses={200: ScrapSalesCategoryMasterSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        scrap_category = self.get_object()
        scrap_category.is_deleted = True
        scrap_category.is_active = False
        scrap_category.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        scrap_category.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)
