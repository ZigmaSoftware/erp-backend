from rest_framework import serializers
from django.db.models import Q

from apps.em_master.models.contractormaster import ContractorMaster, GstType


class ContractorMasterSerializer(serializers.ModelSerializer):
    contractor_code = serializers.ReadOnlyField()

    class Meta:
        model = ContractorMaster
        fields = "__all__"
        read_only_fields = (
            "id",
            "contractor_code",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_deleted",
        )

    def validate(self, attrs):
        instance = self.instance

        gst_type = attrs.get("gst_type", getattr(instance, "gst_type", None))
        gst_no = attrs.get("gst_no", getattr(instance, "gst_no", None))

        if gst_type == GstType.YES and not gst_no:
            raise serializers.ValidationError(
                {"gst_no": "GST number is required when GST type is Yes."}
            )

        if gst_type == GstType.NO:
            attrs["gst_no"] = None

        # ---- Uniqueness checks (soft delete aware) ----
        qs = ContractorMaster.objects.filter(is_deleted=False)

        if instance:
            qs = qs.exclude(id=instance.id)

        if "mobile_no" in attrs and qs.filter(mobile_no=attrs["mobile_no"]).exists():
            raise serializers.ValidationError(
                {"mobile_no": "This mobile number already exists."}
            )

        if attrs.get("phone_no") and qs.filter(phone_no=attrs["phone_no"]).exists():
            raise serializers.ValidationError(
                {"phone_no": "This phone number already exists."}
            )

        if attrs.get("email") and qs.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                {"email": "This email already exists."}
            )

        return attrs

    def create(self, validated_data):
        validated_data["is_active"] = True
        validated_data["is_deleted"] = False
        return super().create(validated_data)
