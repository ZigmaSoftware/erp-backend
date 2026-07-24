from rest_framework import serializers

from apps.sales_transaction.models.work_order import WorkOrderMain, WorkOrderSub, WorkOrderStatusFeed
from apps.sales_transaction.models.sales_order import SalesOrderStatus, SalesOrderTransport
from apps.sales_transaction.models.freight_creation import FreightCreation
from apps.sales_transaction.models.dc_entry import DcEntryForm
from apps.sales_transaction.models.invoice_generation import InvoiceGeneration, InvoiceSub
from apps.sales_transaction.models.payable_entry import PayableEntryMain, PayableEntrySub
from apps.sales_transaction.models.receivable_entry import ReceivableEntry, ReceivableEntrySub


class WorkOrderSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderSub
        exclude = ["is_active", "is_deleted", "created_at", "updated_at"]
        read_only_fields = ["unique_id", "amount", "tot_tax_amnt"]


class WorkOrderMainSerializer(serializers.ModelSerializer):
    sub_items = WorkOrderSubSerializer(many=True, read_only=True)

    class Meta:
        model = WorkOrderMain
        exclude = ["is_active", "is_deleted"]
        read_only_fields = [
            "unique_id", "tot_amount", "net_amt", "tot_qty",
            "work_order_dtc_appr_status", "work_order_appr_status",
            "work_order_dt_appr_status", "send_status",
            "work_status", "work_status_amnt", "paid_status",
            "created_at", "updated_at",
        ]


class WorkOrderStatusFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderStatusFeed
        exclude = ["is_active", "is_deleted", "created_at"]
        read_only_fields = ["unique_id"]


class SalesOrderTransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderTransport
        exclude = ["is_active", "is_deleted", "created_at"]
        read_only_fields = ["unique_id"]


class SalesOrderStatusSerializer(serializers.ModelSerializer):
    transports = SalesOrderTransportSerializer(many=True, read_only=True)

    class Meta:
        model = SalesOrderStatus
        exclude = ["is_active", "is_deleted"]
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class FreightCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreightCreation
        exclude = ["is_active", "is_deleted"]
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class DcEntryFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = DcEntryForm
        exclude = ["is_active", "is_deleted"]
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class InvoiceSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceSub
        exclude = ["is_active", "is_deleted", "created_at", "updated_at"]
        read_only_fields = ["unique_id", "amount"]


class InvoiceGenerationSerializer(serializers.ModelSerializer):
    sub_items = InvoiceSubSerializer(many=True, read_only=True)

    class Meta:
        model = InvoiceGeneration
        exclude = ["is_active", "is_deleted"]
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class PayableEntrySubSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayableEntrySub
        exclude = ["is_active", "is_deleted", "created_at", "updated_at"]
        read_only_fields = ["unique_id"]


class PayableEntryMainSerializer(serializers.ModelSerializer):
    sub_items = PayableEntrySubSerializer(many=True, read_only=True)

    class Meta:
        model = PayableEntryMain
        exclude = ["is_active", "is_deleted"]
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class ReceivableEntrySubSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceivableEntrySub
        exclude = ["is_active", "is_deleted", "created_at", "updated_at"]
        read_only_fields = ["unique_id"]


class ReceivableEntrySerializer(serializers.ModelSerializer):
    sub_items = ReceivableEntrySubSerializer(many=True, read_only=True)

    class Meta:
        model = ReceivableEntry
        exclude = ["is_active", "is_deleted"]
        read_only_fields = ["unique_id", "created_at", "updated_at"]
