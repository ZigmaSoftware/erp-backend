import hashlib
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
        read_only_fields = ["unique_id", "created_at", "updated_at", "document_hash"]

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

    def create(self, validated_data):
        """Create one verification row per submitted file, idempotently.

        The upload dialog can be submitted again after a network timeout. A
        matching active file for the same customer/item/document type is
        returned instead of creating a duplicate verification record.
        """
        document_file = validated_data.get("document_file")
        if document_file:
            document_name = validated_data.get("document_name") or getattr(document_file, "name", "")
            validated_data["document_name"] = document_name
            document_hash = self._document_hash(document_file)
            validated_data["document_hash"] = document_hash

            duplicate = NocDocument.objects.filter(
                scrap_customer_id=validated_data.get("scrap_customer_id"),
                scrap_item_purpose_id=validated_data.get("scrap_item_purpose_id"),
                site_id=validated_data.get("site_id"),
                noc_doc_type_id=validated_data.get("noc_doc_type_id"),
                dispose_type=validated_data.get("dispose_type", ""),
                customer_destination=validated_data.get("customer_destination", ""),
                document_hash=document_hash,
                is_deleted=False,
                document_file__isnull=False,
            ).exclude(document_file="").first()
            if duplicate:
                return duplicate

        return super().create(validated_data)

    def update(self, instance, validated_data):
        document_file = validated_data.get("document_file")
        if document_file:
            validated_data["document_hash"] = self._document_hash(document_file)
        return super().update(instance, validated_data)

    @staticmethod
    def _document_hash(document_file):
        digest = hashlib.sha256()
        current_position = document_file.tell() if hasattr(document_file, "tell") else 0
        if hasattr(document_file, "seek"):
            document_file.seek(0)
        try:
            for chunk in document_file.chunks():
                digest.update(chunk)
        finally:
            if hasattr(document_file, "seek"):
                document_file.seek(current_position)
        return digest.hexdigest()


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
