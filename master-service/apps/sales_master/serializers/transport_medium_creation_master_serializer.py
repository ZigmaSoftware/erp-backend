from rest_framework import serializers

from apps.common_master.validators.unique_name_validator import unique_name_validator
from apps.sales_master.models.transport_medium_creation_master import (
    TransportMediumCreationMaster,
)


class TransportMediumCreationMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransportMediumCreationMaster
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
            Model=TransportMediumCreationMaster,
            name_field="vehicle_name",
            scope_fields=[],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
