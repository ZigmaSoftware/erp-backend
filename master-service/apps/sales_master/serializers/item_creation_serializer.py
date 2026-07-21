from rest_framework import serializers

from apps.common_master.models.site import Site
from apps.sales_master.models.item_creation import ItemCreation
from apps.sales_master.models.item_type_master import ItemTypeMaster
from apps.sales_master.models.scrap_sales_category_master import ScrapSalesCategoryMaster
from apps.common_master.validators.unique_name_validator import unique_name_validator


class ItemCreationSerializer(serializers.ModelSerializer):

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

    site_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=Site.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid site_id."},
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

    site_name = serializers.CharField(
        source="site_id.site_name",
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
            "site_name",
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
