from rest_framework import serializers

from apps.sales_transaction.models.aggregate_entry import AggregateEntryMain, AggregateEntrySub
from apps.sales_transaction.models.afr_transport_entry import AfrTransportEntryMain, AfrTransportEntrySub


# ---------------------------------------------------------------------------
# Aggregate Entry (legacy scrap_entry)
# ---------------------------------------------------------------------------
class AggregateEntrySubSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregateEntrySub
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at", "main"]


class AggregateEntryMainSerializer(serializers.ModelSerializer):
    sub_items = AggregateEntrySubSerializer(many=True, read_only=True)

    class Meta:
        model = AggregateEntryMain
        fields = "__all__"
        read_only_fields = ["unique_id", "scrap_no", "created_at", "updated_at"]


class AggregateEntryCreateSerializer(serializers.Serializer):
    entry_date = serializers.DateField()
    site_id = serializers.UUIDField()
    site_code = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")
    plant_id = serializers.UUIDField(required=False, allow_null=True)
    plant_name = serializers.CharField(required=False, allow_blank=True, default="")
    description = serializers.CharField(required=False, allow_blank=True, default="")
    sub_items = AggregateEntrySubSerializer(many=True)
    created_by = serializers.CharField(max_length=40, required=False, default="")

    def create(self, validated_data):
        from apps.sales_transaction.services.aggregate_entry_service import AggregateEntryService
        return AggregateEntryService.create(validated_data)

    def update(self, instance, validated_data):
        from apps.sales_transaction.services.aggregate_entry_service import AggregateEntryService
        return AggregateEntryService.update(instance, validated_data)


# ---------------------------------------------------------------------------
# AFR Transport Entry (legacy trans_appr_entry)
# ---------------------------------------------------------------------------
class AfrTransportEntrySubSerializer(serializers.ModelSerializer):
    class Meta:
        model = AfrTransportEntrySub
        fields = "__all__"
        # Derived (computed in the model) + relational field are read-only.
        read_only_fields = [
            "unique_id", "created_at", "updated_at", "main",
            "tax_value", "total_freight_cost", "po_tax_value",
            "total_po_value", "net_cost_per_ton",
        ]


class AfrTransportEntryMainSerializer(serializers.ModelSerializer):
    sub_items = AfrTransportEntrySubSerializer(many=True, read_only=True)

    class Meta:
        model = AfrTransportEntryMain
        fields = "__all__"
        read_only_fields = [
            "unique_id", "trans_appr_no", "created_at", "updated_at",
            "approval_status", "approval_date", "approval_by",
        ]


class AfrTransportEntryCreateSerializer(serializers.Serializer):
    entry_date = serializers.DateField()
    site_id = serializers.UUIDField()
    site_code = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")
    customer_id = serializers.UUIDField(required=False, allow_null=True)
    customer_name = serializers.CharField(required=False, allow_blank=True, default="")
    transporter_id = serializers.UUIDField(required=False, allow_null=True)
    transporter_name = serializers.CharField(required=False, allow_blank=True, default="")
    cpcr_no = serializers.CharField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(required=False, allow_blank=True, default="")
    sub_items = AfrTransportEntrySubSerializer(many=True)
    created_by = serializers.CharField(max_length=40, required=False, default="")

    def create(self, validated_data):
        from apps.sales_transaction.services.afr_transport_entry_service import AfrTransportEntryService
        return AfrTransportEntryService.create(validated_data)

    def update(self, instance, validated_data):
        from apps.sales_transaction.services.afr_transport_entry_service import AfrTransportEntryService
        return AfrTransportEntryService.update(instance, validated_data)
