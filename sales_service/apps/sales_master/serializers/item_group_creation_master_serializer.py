from rest_framework import serializers

from apps.common_master.validators.unique_name_validator import unique_name_validator
from apps.sales_master.models.item_group_creation_master import ItemGroupCreationMaster


class ItemGroupCreationMasterSerializer(serializers.ModelSerializer):
    item_type_name = serializers.CharField(source="item_type.item_type", read_only=True)

    class Meta:
        model = ItemGroupCreationMaster
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
            Model=ItemGroupCreationMaster,
            name_field="sub_category_name",
            scope_fields=["item_type"],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
