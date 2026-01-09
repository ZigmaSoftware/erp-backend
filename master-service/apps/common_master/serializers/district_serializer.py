from rest_framework import serializers

from apps.common_master.models.district import District
from apps.common_master.validators.unique_name_validator import unique_name_validator

class DistrictSerializer(serializers.ModelSerializer):
    continent_name = serializers.CharField(source="continent_id.name", read_only=True)
    country_name   = serializers.CharField(source="country_id.name", read_only=True)
    state_name     = serializers.CharField(source="state_id.name", read_only=True)

    class Meta:
        model = District
        fields = "__all__"
        read_only_fields = [
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        validators = []

    def validate(self, attrs):
        return unique_name_validator(
            Model=District,
            scope_fields=["continent_id", "country_id", "state_id"],
        )(self, attrs)
