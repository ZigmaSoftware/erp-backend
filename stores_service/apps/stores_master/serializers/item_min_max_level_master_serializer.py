from rest_framework import serializers

from apps.stores_master.models.item_min_max_level_master import ItemMinMaxLevelMaster
from apps.stores_master.models.item_min_max_type_master import ItemMinMaxTypeMaster


class ItemMinMaxLevelMasterSerializer(serializers.ModelSerializer):

    type = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=ItemMinMaxTypeMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid type."},
    )

    type_name = serializers.CharField(source="type.type_name", read_only=True)

    class Meta:
        model = ItemMinMaxLevelMaster
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "type_name",
        )
        # This table has no single "name" field to dedupe on -- uniqueness is the
        # (type, item_id) pair -- so it can't reuse shared.validators.unique_name_validator
        # (which assumes a string name field). Checked explicitly below instead.
        validators = []

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        item_type = attrs.get("type") or (instance.type if instance else None)
        item_id = attrs.get("item_id") or (instance.item_id if instance else None)

        qs = ItemMinMaxLevelMaster.objects.filter(
            is_deleted=False,
            type=item_type,
            item_id=item_id,
        )
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                {"item_id": "A min/max level already exists for this item under the selected type."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
