from rest_framework import serializers


class ApprovalActionSerializer(serializers.Serializer):
    remarks = serializers.CharField(required=False, allow_blank=True, default="")
    site_id = serializers.UUIDField(required=False, allow_null=True)
