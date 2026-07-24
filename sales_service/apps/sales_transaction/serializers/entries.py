from decimal import Decimal

from rest_framework import serializers

from apps.sales_transaction.models.aggregate_entry import AggregateEntryMain, AggregateEntrySub
from apps.sales_transaction.models.afr_transport_entry import AfrTransportEntryMain, AfrTransportEntrySub


# ---------------------------------------------------------------------------
# Aggregate Entry (legacy scrap_entry)
# ---------------------------------------------------------------------------
class AggregateEntrySubSerializer(serializers.ModelSerializer):
    """Read representation of a stored sub row."""

    class Meta:
        model = AggregateEntrySub
        fields = "__all__"
        read_only_fields = [f.name for f in AggregateEntrySub._meta.fields]


class AggregateEntrySubInputSerializer(serializers.Serializer):
    """
    One editable sub row. Only the UI-editable columns are accepted; the
    reference triple, entry_date, site_name and plant_name are copied from
    the main record by the service.

    ``item_name`` carries the Item/By-Product master **ID**.
    """

    item_name = serializers.CharField(max_length=150)
    stock = serializers.DecimalField(max_digits=15, decimal_places=3, required=False, default=Decimal("0"))
    receipt = serializers.DecimalField(max_digits=15, decimal_places=3)
    remarks = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_receipt(self, value):
        if value is None or value <= Decimal("0"):
            raise serializers.ValidationError("Receipt (kgs) must be greater than zero.")
        return value

    def validate_stock(self, value):
        if value is not None and value < Decimal("0"):
            raise serializers.ValidationError("Stock cannot be negative.")
        return value


class AggregateEntryMainSerializer(serializers.ModelSerializer):
    """
    Read representation. ``site_name`` / ``plant_name`` / (sub) ``item_name``
    hold Master Service IDs; the client resolves the display names.
    """

    sub_items = serializers.SerializerMethodField()

    class Meta:
        model = AggregateEntryMain
        fields = "__all__"
        read_only_fields = [f.name for f in AggregateEntryMain._meta.fields]

    def get_sub_items(self, obj):
        rows = AggregateEntrySub.objects.filter(
            random_no=obj.random_no,
            random_sc=obj.random_sc,
            scrap_no=obj.scrap_no,
            is_deleted=False,
        )
        return AggregateEntrySubSerializer(rows, many=True).data


class AggregateEntryCreateSerializer(serializers.Serializer):
    entry_date = serializers.DateField()
    site_name = serializers.CharField(max_length=150)
    plant_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    description = serializers.CharField(required=False, allow_blank=True, default="")
    sub_items = AggregateEntrySubInputSerializer(many=True)
    created_by = serializers.CharField(max_length=40, required=False, default="")
    updated_by = serializers.CharField(max_length=40, required=False, default="")

    def validate_sub_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one By-Product row is required.")
        return value

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
