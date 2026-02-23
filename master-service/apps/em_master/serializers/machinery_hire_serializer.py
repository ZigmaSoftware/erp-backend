from rest_framework import serializers

from apps.common_master.models.site import Site
from apps.em_master.models.equipment_modelmaster import EquipmentModelMaster
from apps.em_master.models.equipment_typemaster import EquipmentTypeMaster
from apps.em_master.models.machinery_hire import MachineryHire
from apps.em_master.models.vehicle_creation import VehicleCreation


class MachineryHireSerializer(serializers.ModelSerializer):
    site = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=Site.objects.filter(is_deleted=False),
    )
    equipment_type = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=EquipmentTypeMaster.objects.filter(is_deleted=False),
    )
    equipment_model = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=EquipmentModelMaster.objects.filter(is_deleted=False),
    )
    vehicle = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=VehicleCreation.objects.filter(is_deleted=False),
    )

    class Meta:
        model = MachineryHire
        fields = [
            "id",
            "unique_id",
            "site",
            "date",
            "diesel_status",
            "equipment_type",
            "equipment_model",
            "vehicle",
            "hire_rate",
            "unit",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = [
            "id",
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

    def _resolve_existing(self, attrs, field_name):
        if field_name in attrs:
            return attrs[field_name]
        if self.instance:
            return getattr(self.instance, field_name)
        return None

    def validate(self, attrs):
        site = self._resolve_existing(attrs, "site")
        vehicle = self._resolve_existing(attrs, "vehicle")
        equipment_model = self._resolve_existing(attrs, "equipment_model")
        equipment_type = self._resolve_existing(attrs, "equipment_type")

        errors = {}

        if vehicle:
            if not vehicle.is_active:
                errors["vehicle"] = "Selected vehicle is inactive."
            if site and vehicle.site and site != vehicle.site:
                errors["site"] = "Selected site must match vehicle's site."

        if equipment_model and equipment_type:
            if equipment_model.equipment_type != equipment_type:
                errors["equipment_model"] = (
                    "Selected equipment model does not belong to the chosen type."
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def _ensure_equipment_type(self, attrs):
        equipment_model = attrs.get("equipment_model")
        if equipment_model:
            attrs["equipment_type"] = equipment_model.equipment_type
        return attrs

    def create(self, validated_data):
        validated_data = self._ensure_equipment_type(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._ensure_equipment_type(validated_data)
        return super().update(instance, validated_data)
