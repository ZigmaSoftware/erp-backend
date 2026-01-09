from rest_framework import serializers

from apps.common_master.models.plant import Plant
from apps.common_master.validators.unique_name_validator import unique_name_validator


class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
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
            Model=Plant,
            name_field="plant_name",
            scope_fields=["site_id"],
        )(self, attrs)
