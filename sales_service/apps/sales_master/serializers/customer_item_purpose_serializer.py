from rest_framework import serializers

from apps.sales_master.models.customer_creation_master import CustomerCreationMaster
from apps.sales_master.models.customer_item_purpose import CustomerItemPurpose
from apps.sales_master.models.item_creation import ItemCreation


class CustomerItemPurposeSerializer(serializers.ModelSerializer):
    """
    `site` holds a plain Master Service Site `unique_id` value (no local DB
    relation - see SALES_SERVICE_README.md). Display name is resolved
    client-side from Master Service's own site API.
    """

    customer = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=CustomerCreationMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid customer."},
    )

    item = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=ItemCreation.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid item."},
    )

    item_name = serializers.CharField(source="item.item_name", read_only=True)

    class Meta:
        model = CustomerItemPurpose
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "item_name",
        )
        validators = []

    def validate(self, attrs):
        customer = attrs.get("customer", getattr(self.instance, "customer", None))
        site = attrs.get("site", getattr(self.instance, "site", None))
        destination = attrs.get(
            "destination", getattr(self.instance, "destination", None)
        )
        item = attrs.get("item", getattr(self.instance, "item", None))

        duplicates = CustomerItemPurpose.objects.filter(
            is_deleted=False,
            customer=customer,
            site=site,
            destination__iexact=(destination or "").strip(),
            item=item,
        )
        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise serializers.ValidationError(
                "This item already exists for the selected site and destination."
            )

        return attrs

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
