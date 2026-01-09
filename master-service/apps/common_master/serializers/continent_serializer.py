from rest_framework import serializers

from apps.common_master.models.continent import Continent
from apps.common_master.validators.unique_name_validator import unique_name_validator

class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
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
            Model=Continent,
            name_field="name",
        )(self, attrs)
