from rest_framework import serializers

from apps.stores_master.models.supplier_creation_master import SupplierCreationMaster
from apps.stores_master.models.supplier_supporting_document import (
    SupplierSupportingDocument,
)


class SupplierSupportingDocumentSerializer(serializers.ModelSerializer):

    supplier = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=SupplierCreationMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid supplier."},
    )

    class Meta:
        model = SupplierSupportingDocument
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
