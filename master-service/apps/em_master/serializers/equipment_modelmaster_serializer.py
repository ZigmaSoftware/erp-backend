from rest_framework import serializers

from apps.em_master.models.equipment_modelmaster import EquipmentModelMaster
from apps.em_master.validators.unique_name_validator import unique_name_validator


class EquipmentModelMasterSerializer(serializers.ModelSerializer):
    equipment_type_name = serializers.CharField(
    source="equipment_type.name",
    read_only=True
)

    class Meta:
        model = EquipmentModelMaster
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_deleted",
        )

    def validate(self, attrs):
        """
        Ensure model_name is unique per equipment_type
        """
        return unique_name_validator(
            Model=EquipmentModelMaster,
            name_field="model_name",
            scope_fields=["equipment_type"],
        )(self, attrs)

    def create(self, validated_data):
        """
        Force new records to be active
        """
        validated_data["is_active"] = True
        validated_data["is_deleted"] = False
        return super().create(validated_data)
