from rest_framework import serializers

from apps.common_master.validators.unique_name_validator import unique_name_validator
from apps.sales_master.models.terms_of_payment_creation_master import (
    TermsOfPaymentCreationMaster,
)


class TermsOfPaymentCreationMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = TermsOfPaymentCreationMaster
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
            Model=TermsOfPaymentCreationMaster,
            name_field="terms_of_payment",
            scope_fields=[],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
