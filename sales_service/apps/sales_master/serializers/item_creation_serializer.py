from rest_framework import serializers

from apps.sales_master.models.item_creation import ItemCreation
from apps.sales_master.models.item_type_master import ItemTypeMaster
from apps.sales_master.models.scrap_sales_category_master import ScrapSalesCategoryMaster
from apps.common_master.validators.unique_name_validator import unique_name_validator


class ItemCreationSerializer(serializers.ModelSerializer):
    """
    `site_id` holds a plain Master Service Site `unique_id` value (no local
    DB relation - see SALES_SERVICE_README.md). Display name is resolved
    client-side from Master Service's own site API.
    """

    # -----------------------------------------
    # ForeignKey Fields (accept unique_id)
    # -----------------------------------------

    item_type_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=ItemTypeMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid item_type_id."},
    )

    category_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=ScrapSalesCategoryMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid category_id."},
    )

    # -----------------------------------------
    # Name Fields (GET only)
    # -----------------------------------------

    item_type_name = serializers.CharField(
        source="item_type_id.item_type",
        read_only=True,
    )

    category_name = serializers.CharField(
        source="category_id.category_name",
        read_only=True,
    )

    # Derived from the row's auto-increment id, never stored.
    item_code = serializers.ReadOnlyField()

    class Meta:
        model = ItemCreation
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "item_code",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "item_type_name",
            "category_name",
        )
        validators = []

    def validate(self, attrs):
        return unique_name_validator(
            Model=ItemCreation,
            name_field="item_name",
            scope_fields=["item_type_id", "category_id"],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
