from rest_framework import serializers

from apps.common_master.models.site import Site
from apps.em_master.models.equipment_modelmaster import EquipmentModelMaster
from apps.em_master.models.equipment_typemaster import EquipmentTypeMaster
from apps.em_master.models.machinery_hire import MachineryHire
from apps.em_master.models.vehicle_creation import VehicleCreation


class MachineryHireSerializer(serializers.ModelSerializer):

    site_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=Site.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid site_id."},
    )

    equipment_type_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=EquipmentTypeMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid equipment_type_id."},
    )

    equipment_model_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=EquipmentModelMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid equipment_model_id."},
    )

    vehicle_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=VehicleCreation.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid vehicle_id."},
    )

    # Read-only display fields
    site_name = serializers.CharField(source="site_id.site_name", read_only=True)
    equipment_type_name = serializers.CharField(source="equipment_type_id.name", read_only=True)
    equipment_model_name = serializers.CharField(source="equipment_model_id.model_name", read_only=True)
    vehicle_code = serializers.CharField(source="vehicle_id.vehicle_code", read_only=True)

    class Meta:
        model = MachineryHire
        fields = "__all__"

        read_only_fields = [
            "id",
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "site_name",
            "equipment_type_name",
            "equipment_model_name",
            "vehicle_code",
        ]

    def validate(self, attrs):

        site = attrs.get("site_id", getattr(self.instance, "site_id", None))
        vehicle = attrs.get("vehicle_id", getattr(self.instance, "vehicle_id", None))
        print("vehcicle",vehicle.site_id.site_name)
        equipment_model = attrs.get("equipment_model_id", getattr(self.instance, "equipment_model_id", None))
        equipment_type = attrs.get("equipment_type_id", getattr(self.instance, "equipment_type_id", None))

        errors = {}

        if vehicle and not vehicle.is_active:
            errors["vehicle_id"] = "Selected vehicle is inactive."

        if vehicle and site:
            if getattr(vehicle, "site", None) and vehicle.site.unique_id != site.unique_id:
                errors["site_id"] = "Selected site must match vehicle's site."

        if equipment_model and equipment_type:
            if equipment_model.equipment_type_id != equipment_type.unique_id:
                errors["equipment_model_id"] = (
                    "Selected equipment model does not belong to chosen type."
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
