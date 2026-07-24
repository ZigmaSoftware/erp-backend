from rest_framework import serializers

from apps.sales_shared.models.approval_status import ApprovalHistory


class ApprovalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalHistory
        fields = "__all__"
        read_only_fields = fields


class ApprovalActionSerializer(serializers.Serializer):
    remarks = serializers.CharField(required=False, allow_blank=True, default="")
