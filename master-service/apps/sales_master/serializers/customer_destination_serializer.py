from rest_framework import serializers

from apps.common_master.models.site import Site
from apps.sales_master.models.customer_creation_master import CustomerCreationMaster
from apps.sales_master.models.customer_destination import CustomerDestination


class CustomerDestinationSerializer(serializers.ModelSerializer):

    customer = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=CustomerCreationMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid customer."},
    )

    site = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=Site.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid site."},
    )

    site_name = serializers.CharField(source="site.site_name", read_only=True)

    class Meta:
        model = CustomerDestination
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "site_name",
        )
        validators = []

    def validate(self, attrs):
        customer = attrs.get("customer", getattr(self.instance, "customer", None))
        site = attrs.get("site", getattr(self.instance, "site", None))
        destination = attrs.get(
            "destination", getattr(self.instance, "destination", None)
        )

        duplicates = CustomerDestination.objects.filter(
            is_deleted=False,
            customer=customer,
            site=site,
            destination__iexact=(destination or "").strip(),
        )
        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise serializers.ValidationError(
                "This destination already exists for the selected site."
            )

        return attrs

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
