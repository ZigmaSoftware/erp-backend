from rest_framework import serializers

from apps.stores_master.models.supplier_creation_master import SupplierCreationMaster
from shared.validators import unique_name_validator


class SupplierCreationMasterSerializer(serializers.ModelSerializer):
    # DRF auto-attaches a field-level UniqueValidator from the model's
    # UniqueConstraint, which runs before (and short-circuits) validate()
    # below -- overriding it here with validators=[] ensures the explicit
    # case-insensitive check in validate() is what actually enforces
    # uniqueness, rather than relying on the DB column's collation.
    party_name = serializers.CharField(max_length=100, validators=[])

    class Meta:
        model = SupplierCreationMaster
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "supplier_code",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
        validators = []

    def validate_sites(self, value):
        if not value:
            raise serializers.ValidationError("At least one site must be assigned.")
        return value

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        has_gst = attrs.get("has_gst", instance.has_gst if instance else False)
        gst_no = attrs.get("gst_no", instance.gst_no if instance else None)
        if has_gst and not gst_no:
            raise serializers.ValidationError(
                {"gst_no": "GST number is required when GST is applicable."}
            )

        return unique_name_validator(
            Model=SupplierCreationMaster,
            name_field="party_name",
            scope_fields=["mobile_no"],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
