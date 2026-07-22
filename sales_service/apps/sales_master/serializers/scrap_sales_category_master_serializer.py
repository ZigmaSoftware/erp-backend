from rest_framework import serializers

from apps.sales_master.models.scrap_sales_category_master import ScrapSalesCategoryMaster
from apps.common_master.validators.unique_name_validator import unique_name_validator


class ScrapSalesCategoryMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScrapSalesCategoryMaster
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
        validators = []

    def validate(self, attrs):
        return unique_name_validator(
            Model=ScrapSalesCategoryMaster,
            name_field="category_name",
            scope_fields=[],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
