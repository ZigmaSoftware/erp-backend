from rest_framework import serializers

from apps.em_master.models.equipment_typemaster import EquipmentTypeMaster
from apps.em_master.validators.unique_name_validator import unique_name_validator


class EquipmentTypeMasterSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = EquipmentTypeMaster
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
        validators = []

    def validate(self, attrs):
        return unique_name_validator(
            Model=EquipmentTypeMaster,
            name_field="name",
            scope_fields=["category"],
        )(self, attrs)
