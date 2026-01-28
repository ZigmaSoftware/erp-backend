from rest_framework import serializers

from apps.em_master.models.vehicle_suppliermaster import VehicleSupplierMaster
from apps.em_master.validators.unique_name_validator import unique_name_validator


class VehicleSupplierMasterSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = VehicleSupplierMaster
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

    def validate(self, attrs):
        return unique_name_validator(
            Model=VehicleSupplierMaster,
            name_field="supplier_name",  
            scope_fields=[],
        )(self, attrs)

    def create(self, validated_data):
        validated_data["is_active"] = True
        return super().create(validated_data)
