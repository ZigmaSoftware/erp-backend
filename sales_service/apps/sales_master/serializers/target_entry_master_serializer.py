from rest_framework import serializers

from apps.sales_master.models.target_entry_master import TargetEntryMaster
from apps.sales_master.serializers.target_entry_item_serializer import (
    TargetEntryItemSerializer,
)


class TargetEntryMasterSerializer(serializers.ModelSerializer):
    """
    `site_id` holds a plain Master Service Site `unique_id` value (no local
    DB relation - see SALES_SERVICE_README.md). Display name is resolved
    client-side from Master Service's own site API.
    """

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
            "items",
        )
        validators = []

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
