from rest_framework import serializers

from apps.sales_master.models.item_type_master import ItemTypeMaster
from apps.sales_master.models.sub_category_master import SubCategoryMaster
from apps.sales_master.models.target_entry_item import TargetEntryItem
from apps.sales_master.models.target_entry_master import TargetEntryMaster


class TargetEntryItemSerializer(serializers.ModelSerializer):

    target_entry = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=TargetEntryMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid target_entry."},
    )

    item_type = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=ItemTypeMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid item_type."},
    )

    sub_category = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=SubCategoryMaster.objects.filter(is_deleted=False),
        required=False,
        allow_null=True,
        error_messages={"does_not_exist": "Invalid sub_category."},
    )

    target_no = serializers.CharField(source="target_entry.target_no", read_only=True)
    item_type_name = serializers.CharField(source="item_type.item_type", read_only=True)
    sub_category_name = serializers.CharField(
        source="sub_category.sub_category_name", read_only=True, default=None
    )

    class Meta:
        model = TargetEntryItem
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "random_no",
            "random_sc",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "target_no",
            "item_type_name",
            "sub_category_name",
        )
        validators = []

    def validate(self, attrs):
        target_entry = attrs.get(
            "target_entry", getattr(self.instance, "target_entry", None)
        )
        item_type = attrs.get("item_type", getattr(self.instance, "item_type", None))
        sub_category = attrs.get(
            "sub_category", getattr(self.instance, "sub_category", None)
        )
        target_qty = attrs.get(
            "target_qty", getattr(self.instance, "target_qty", None)
        )
        expense_amount = attrs.get(
            "expense_amount", getattr(self.instance, "expense_amount", 0)
        )
        revenue_amount = attrs.get(
            "revenue_amount", getattr(self.instance, "revenue_amount", 0)
        )

        duplicates = TargetEntryItem.objects.filter(
            is_deleted=False,
            target_entry=target_entry,
            item_type=item_type,
            sub_category=sub_category,
            target_qty=target_qty,
            expense_amount=expense_amount,
            revenue_amount=revenue_amount,
        )
        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise serializers.ValidationError(
                "This item already exists in this target entry."
            )

        return attrs

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
