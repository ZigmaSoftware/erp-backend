from rest_framework import serializers

from apps.sales_master.models.document_type_master import DocumentTypeMaster


class DocumentTypeMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentTypeMaster
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
        validators = []

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
