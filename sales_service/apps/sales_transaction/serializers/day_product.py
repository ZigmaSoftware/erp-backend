import re

from rest_framework import serializers
from apps.sales_transaction.models.aggregate_quotation import AggregateQuotationMain, AggregateQuotationSub
from apps.sales_transaction.models.scrap_quotation import ScrapQuotationMain, ScrapQuotationSub
from apps.sales_transaction.models.noc_document import NocDocument, NocDocumentApprovalHistory
from apps.sales_transaction.models.daily_target_disposal import DailyTargetDisposalMain, DailyTargetDisposalSub
from apps.sales_transaction.models.afr_transport_rfq import AfrTransportRfq


class AggregateQuotationSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregateQuotationSub
        fields = "__all__"
        # `main` is set by the service during nested create; it must not be
        # required on the inbound sub payload.
        read_only_fields = ["unique_id", "created_at", "updated_at", "main"]


class AggregateQuotationMainSerializer(serializers.ModelSerializer):
    sub_items = AggregateQuotationSubSerializer(many=True, read_only=True)

    class Meta:
        model = AggregateQuotationMain
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class AggregateQuotationCreateSerializer(serializers.Serializer):
    party_name = serializers.CharField(max_length=255)
    party_mobile_no = serializers.CharField(max_length=20)
    party_address = serializers.CharField(required=False, allow_blank=True, default="")
    site_id = serializers.UUIDField()
    # Site invoice-head code used to build the legacy document number; optional
    # because the head is master data owned outside this service.
    site_code = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")
    quote_month = serializers.CharField(max_length=20)
    main_description = serializers.CharField(required=False, allow_blank=True, default="")
    quote_file = serializers.CharField(required=False, allow_blank=True, default="")
    sub_items = AggregateQuotationSubSerializer(many=True)
    created_by = serializers.CharField(max_length=40, required=False, default="")

    def validate_party_mobile_no(self, value):
        # PHP enforces exactly 10 digits (aggregate_quotation_entry.js:625-628).
        if not re.fullmatch(r"\d{10}", value or ""):
            raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
        return value

    def create(self, validated_data):
        from apps.sales_transaction.services.aggregate_quotation_service import AggregateQuotationService
        return AggregateQuotationService.create(validated_data)

    def update(self, instance, validated_data):
        from apps.sales_transaction.services.aggregate_quotation_service import AggregateQuotationService
        return AggregateQuotationService.update(instance, validated_data)


class ScrapQuotationSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapQuotationSub
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at", "tot_amount", "main"]


class ScrapQuotationMainSerializer(serializers.ModelSerializer):
    sub_items = ScrapQuotationSubSerializer(many=True, read_only=True)

    class Meta:
        model = ScrapQuotationMain
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class ScrapQuotationCreateSerializer(serializers.Serializer):
    party_name = serializers.CharField(max_length=255)
    party_mobile_no = serializers.CharField(max_length=20)
    party_address = serializers.CharField(required=False, allow_blank=True, default="")
    site_id = serializers.UUIDField()
    site_code = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")
    quote_month = serializers.CharField(max_length=20)
    main_description = serializers.CharField(required=False, allow_blank=True, default="")
    quote_file = serializers.CharField(required=False, allow_blank=True, default="")
    sub_items = ScrapQuotationSubSerializer(many=True)
    created_by = serializers.CharField(max_length=40, required=False, default="")

    def validate_party_mobile_no(self, value):
        # PHP enforces exactly 10 digits (scrap_quotation_entry.js validation).
        if not re.fullmatch(r"\d{10}", value or ""):
            raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
        return value

    def create(self, validated_data):
        from apps.sales_transaction.services.scrap_quotation_service import ScrapQuotationService
        return ScrapQuotationService.create(validated_data)

    def update(self, instance, validated_data):
        from apps.sales_transaction.services.scrap_quotation_service import ScrapQuotationService
        return ScrapQuotationService.update(instance, validated_data)


class NocDocumentApprovalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NocDocumentApprovalHistory
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at"]


class NocDocumentSerializer(serializers.ModelSerializer):
    approval_history = NocDocumentApprovalHistorySerializer(many=True, read_only=True)

    # PHP limits: max 15 MB, extensions jpg/jpeg/png/pdf
    # (scrap_customer_creation/file_upload_list.php:44, doc_upload.php:207,322).
    NOC_MAX_UPLOAD_BYTES = 15 * 1024 * 1024
    NOC_ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}

    class Meta:
        model = NocDocument
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]

    def validate_document_file(self, value):
        if not value:
            return value
        if value.size > self.NOC_MAX_UPLOAD_BYTES:
            raise serializers.ValidationError("File too large. Maximum allowed size is 15 MB.")
        ext = value.name.rsplit(".", 1)[-1].lower() if "." in value.name else ""
        if ext not in self.NOC_ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                "Unsupported file type. Allowed: jpg, jpeg, png, pdf."
            )
        return value


class DailyTargetDisposalSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyTargetDisposalSub
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at", "main"]


class DailyTargetDisposalMainSerializer(serializers.ModelSerializer):
    sub_items = DailyTargetDisposalSubSerializer(many=True, read_only=True)

    class Meta:
        model = DailyTargetDisposalMain
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]


class DailyTargetDisposalCreateSerializer(serializers.Serializer):
    site_id = serializers.UUIDField()
    site_code = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")
    entry_date = serializers.DateField()
    sub_items = DailyTargetDisposalSubSerializer(many=True)
    created_by = serializers.CharField(max_length=40, required=False, default="")

    def create(self, validated_data):
        from apps.sales_transaction.services.daily_target_service import DailyTargetService
        return DailyTargetService.create(validated_data)

    def update(self, instance, validated_data):
        from apps.sales_transaction.services.daily_target_service import DailyTargetService
        return DailyTargetService.update(instance, validated_data)


class AfrTransportRfqSerializer(serializers.ModelSerializer):
    class Meta:
        model = AfrTransportRfq
        fields = "__all__"
        read_only_fields = ["unique_id", "created_at", "updated_at"]
