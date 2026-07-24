from rest_framework import serializers
from apps.sales_transaction.models.icw_work_order import IcwWorkOrder, IcwWorkOrderTransport
from apps.sales_transaction.models.negative_invoice import NegativeInvoice, NegativeInvoiceSub
from apps.sales_transaction.models.freight_letter import FreightLetter
from apps.sales_transaction.models.co_processing import CoProcessingCertificate
from apps.sales_transaction.models.aggregate_comparison import AggregateComparison, AggregateComparisonSub
from apps.sales_transaction.models.scrap_quotation_comparison import ScrapQuotationComparison, ScrapQuotationComparisonSub
from apps.sales_transaction.models.confirmation_receipt import ConfirmationReceiptDc, ConfirmationReceiptImage


class IcwWorkOrderTransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = IcwWorkOrderTransport
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class IcwWorkOrderSerializer(serializers.ModelSerializer):
    transports = IcwWorkOrderTransportSerializer(many=True, read_only=True)

    class Meta:
        model = IcwWorkOrder
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class NegativeInvoiceSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegativeInvoiceSub
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class NegativeInvoiceSerializer(serializers.ModelSerializer):
    sub_items = NegativeInvoiceSubSerializer(many=True, read_only=True)

    class Meta:
        model = NegativeInvoice
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class FreightLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreightLetter
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class CoProcessingCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoProcessingCertificate
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class AggregateComparisonSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregateComparisonSub
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class AggregateComparisonSerializer(serializers.ModelSerializer):
    sub_items = AggregateComparisonSubSerializer(many=True, read_only=True)

    class Meta:
        model = AggregateComparison
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class ScrapQuotationComparisonSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapQuotationComparisonSub
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class ScrapQuotationComparisonSerializer(serializers.ModelSerializer):
    sub_items = ScrapQuotationComparisonSubSerializer(many=True, read_only=True)

    class Meta:
        model = ScrapQuotationComparison
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class ConfirmationReceiptImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfirmationReceiptImage
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at"]


class ConfirmationReceiptDcSerializer(serializers.ModelSerializer):
    images = ConfirmationReceiptImageSerializer(many=True, read_only=True)

    class Meta:
        model = ConfirmationReceiptDc
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]
