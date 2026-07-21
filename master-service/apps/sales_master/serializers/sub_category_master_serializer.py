from rest_framework import serializers

from apps.common_master.validators.unique_name_validator import unique_name_validator
from apps.sales_master.models.item_type_master import ItemTypeMaster
from apps.sales_master.models.sub_category_master import SubCategoryMaster


class SubCategoryMasterSerializer(serializers.ModelSerializer):

    item_type = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=ItemTypeMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid item_type."},
    )

    item_type_name = serializers.CharField(source="item_type.item_type", read_only=True)

    class Meta:
        model = SubCategoryMaster
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "item_type_name",
        )
        validators = []

    def validate(self, attrs):
        return unique_name_validator(
            Model=SubCategoryMaster,
            name_field="sub_category_name",
            scope_fields=["item_type"],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
