from rest_framework import serializers

from apps.common_master.validators.unique_name_validator import unique_name_validator
from apps.sales_master.models.mail_details_creation_master import (
    MailDetailsCreationMaster,
)


class MailDetailsCreationMasterSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source="site.site_name", read_only=True)

    class Meta:
        model = MailDetailsCreationMaster
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
            Model=MailDetailsCreationMaster,
            name_field="mail_type",
            scope_fields=["site"],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
