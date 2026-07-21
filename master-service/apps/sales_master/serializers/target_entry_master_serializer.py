from rest_framework import serializers

from apps.common_master.models.site import Site
from apps.sales_master.models.target_entry_master import TargetEntryMaster
from apps.sales_master.serializers.target_entry_item_serializer import (
    TargetEntryItemSerializer,
)


class TargetEntryMasterSerializer(serializers.ModelSerializer):

    site_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=Site.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid site_id."},
    )

    site_name = serializers.CharField(source="site_id.site_name", read_only=True)
    items = TargetEntryItemSerializer(many=True, read_only=True)

    class Meta:
        model = TargetEntryMaster
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "random_no",
            "random_sc",
            "tot_target",
            "tot_expense",
            "tot_revenue",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "site_name",
            "items",
        )
        validators = []

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
