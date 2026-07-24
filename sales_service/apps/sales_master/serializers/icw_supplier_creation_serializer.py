from rest_framework import serializers

from apps.common_master.validators.unique_name_validator import unique_name_validator
from apps.sales_master.models.icw_supplier_creation import IcwSupplierCreation


class IcwSupplierCreationSerializer(serializers.ModelSerializer):
    """
    country_id / state_id / district_id / city_id / sites hold plain Master
    Service `unique_id` values (no local DB relation - see
    SALES_SERVICE_README.md). Display names are resolved client-side from
    Master Service's own country/state/district/city/site APIs.
    """

    class Meta:
        model = IcwSupplierCreation
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "supplier_id",
            "random_no",
            "random_sc",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
        validators = []

    def validate(self, attrs):
        has_gst = attrs.get("has_gst", getattr(self.instance, "has_gst", False))
        gst_no = attrs.get("gst_no", getattr(self.instance, "gst_no", None))
        if has_gst and not gst_no:
            raise serializers.ValidationError(
                {"gst_no": "GST number is required when GST is Yes."}
            )

        return unique_name_validator(
            Model=IcwSupplierCreation,
            name_field="supplier_name",
            scope_fields=[],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return IcwSupplierCreation.objects.create(**validated_data)
