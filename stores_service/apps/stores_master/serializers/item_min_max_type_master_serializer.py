from rest_framework import serializers

from apps.stores_master.models.item_min_max_type_master import ItemMinMaxTypeMaster
from shared.validators import unique_name_validator


class ItemMinMaxTypeMasterSerializer(serializers.ModelSerializer):
    # DRF auto-attaches a field-level UniqueValidator from the model's
    # UniqueConstraint, which runs before (and short-circuits) validate()
    # below -- overriding it here with validators=[] ensures the explicit
    # case-insensitive check in validate() is what actually enforces
    # uniqueness, rather than relying on the DB column's collation.
    type_name = serializers.CharField(max_length=100, validators=[])

    class Meta:
        model = ItemMinMaxTypeMaster
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
            Model=ItemMinMaxTypeMaster,
            name_field="type_name",
            scope_fields=[],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
