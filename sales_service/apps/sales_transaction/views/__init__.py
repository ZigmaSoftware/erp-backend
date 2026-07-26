from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.common_master.authentication.header_auth import GatewayHeaderAuthentication
from apps.sales_transaction.models.work_order import WorkOrderMain
from apps.sales_transaction.models.sales_order import SalesOrderStatus
from apps.sales_transaction.models.freight_creation import FreightCreation
from apps.sales_transaction.models.dc_entry import DcEntryForm
from apps.sales_transaction.models.invoice_generation import InvoiceGeneration
from apps.sales_transaction.models.payable_entry import PayableEntryMain
from apps.sales_transaction.models.receivable_entry import ReceivableEntry
from apps.sales_transaction.models.aggregate_quotation import AggregateQuotationMain
from apps.sales_transaction.models.scrap_quotation import ScrapQuotationMain
from apps.sales_transaction.models.noc_document import NocDocument
from apps.sales_transaction.models.daily_target_disposal import DailyTargetDisposalMain
from apps.sales_transaction.models.afr_transport_rfq import AfrTransportRfq
from apps.sales_transaction.models.icw_work_order import IcwWorkOrder
from apps.sales_transaction.models.negative_invoice import NegativeInvoice
from apps.sales_transaction.models.freight_letter import FreightLetter
from apps.sales_transaction.models.co_processing import CoProcessingCertificate
from apps.sales_transaction.models.aggregate_comparison import AggregateComparison
from apps.sales_transaction.models.scrap_quotation_comparison import ScrapQuotationComparison
from apps.sales_transaction.models.confirmation_receipt import ConfirmationReceiptDc
from apps.sales_transaction.models.aggregate_entry import AggregateEntryMain
from apps.sales_transaction.models.afr_transport_entry import AfrTransportEntryMain

from apps.sales_transaction.serializers import (
    WorkOrderMainSerializer, SalesOrderStatusSerializer,
    FreightCreationSerializer, DcEntryFormSerializer,
    InvoiceGenerationSerializer, PayableEntryMainSerializer,
    ReceivableEntrySerializer,
)
from apps.sales_transaction.serializers.day_product import (
    AggregateQuotationMainSerializer, AggregateQuotationCreateSerializer,
    ScrapQuotationMainSerializer, ScrapQuotationCreateSerializer,
    NocDocumentSerializer,
    DailyTargetDisposalMainSerializer, DailyTargetDisposalCreateSerializer,
    AfrTransportRfqSerializer,
)
from apps.sales_transaction.serializers.phase_a import (
    IcwWorkOrderSerializer, NegativeInvoiceSerializer,
    FreightLetterSerializer, CoProcessingCertificateSerializer,
    AggregateComparisonSerializer, ScrapQuotationComparisonSerializer,
    ConfirmationReceiptDcSerializer,
)
from apps.sales_transaction.serializers.entries import (
    AggregateEntryMainSerializer, AggregateEntryCreateSerializer,
    AfrTransportEntryMainSerializer, AfrTransportEntryCreateSerializer,
)
from apps.sales_transaction.filters import (
    WorkOrderFilter, SalesOrderFilter, FreightFilter,
    DcEntryFilter, InvoiceFilter, PayableFilter,
)
from apps.sales_transaction.filters.day_product_filters import (
    AggregateQuotationFilter, ScrapQuotationFilter, NocDocumentFilter,
    DailyTargetDisposalFilter, AfrTransportRfqFilter,
    AggregateEntryFilter, AfrTransportEntryFilter,
)
from apps.sales_transaction.filters.phase_a_filters import (
    IcwWorkOrderFilter, NegativeInvoiceFilter, FreightLetterFilter,
    CoProcessingFilter, AggregateComparisonFilter,
    ScrapQuotationComparisonFilter, ConfirmationReceiptFilter,
)


class WorkOrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = WorkOrderMain.objects.filter(is_deleted=False)
    serializer_class = WorkOrderMainSerializer
    filterset_class = WorkOrderFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SalesOrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = SalesOrderStatus.objects.filter(is_deleted=False)
    serializer_class = SalesOrderStatusSerializer
    filterset_class = SalesOrderFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.is_active = False
        instance.save(update_fields=["is_deleted", "is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class FreightViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FreightCreation.objects.filter(is_deleted=False)
    serializer_class = FreightCreationSerializer
    filterset_class = FreightFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(add_user=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(edit_user=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DcEntryViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = DcEntryForm.objects.filter(is_deleted=False)
    serializer_class = DcEntryFormSerializer
    filterset_class = DcEntryFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(add_user=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(edit_user=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvoiceViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = InvoiceGeneration.objects.filter(is_deleted=False)
    serializer_class = InvoiceGenerationSerializer
    filterset_class = InvoiceFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(add_user=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(edit_user=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PayableViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PayableEntryMain.objects.filter(is_deleted=False)
    serializer_class = PayableEntryMainSerializer
    filterset_class = PayableFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(add_user=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(edit_user=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReceivableViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ReceivableEntry.objects.filter(is_deleted=False)
    serializer_class = ReceivableEntrySerializer
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AggregateQuotationViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AggregateQuotationMain.objects.filter(is_deleted=False)
    filterset_class = AggregateQuotationFilter
    lookup_field = "unique_id"

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return AggregateQuotationCreateSerializer
        return AggregateQuotationMainSerializer

    def create(self, request, *args, **kwargs):
        ser = AggregateQuotationCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        main = ser.save()
        return Response(AggregateQuotationMainSerializer(main).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = AggregateQuotationCreateSerializer(instance, data=request.data, partial=kwargs.get("partial", False))
        ser.is_valid(raise_exception=True)
        main = ser.save()
        return Response(AggregateQuotationMainSerializer(main).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScrapQuotationViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ScrapQuotationMain.objects.filter(is_deleted=False)
    filterset_class = ScrapQuotationFilter
    lookup_field = "unique_id"

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ScrapQuotationCreateSerializer
        return ScrapQuotationMainSerializer

    def create(self, request, *args, **kwargs):
        ser = ScrapQuotationCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        main = ser.save()
        return Response(ScrapQuotationMainSerializer(main).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = ScrapQuotationCreateSerializer(instance, data=request.data, partial=kwargs.get("partial", False))
        ser.is_valid(raise_exception=True)
        main = ser.save()
        return Response(ScrapQuotationMainSerializer(main).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NocDocumentViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = NocDocument.objects.filter(is_deleted=False)
    serializer_class = NocDocumentSerializer
    filterset_class = NocDocumentFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.headers.get("X-Username", ""),
            staff_id=self.request.headers.get("X-Username", ""),
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.is_active = False
        instance.save(update_fields=["is_deleted", "is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class DailyTargetDisposalViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = DailyTargetDisposalMain.objects.filter(is_deleted=False)
    filterset_class = DailyTargetDisposalFilter
    lookup_field = "unique_id"

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return DailyTargetDisposalCreateSerializer
        return DailyTargetDisposalMainSerializer

    def create(self, request, *args, **kwargs):
        ser = DailyTargetDisposalCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        main = ser.save()
        return Response(DailyTargetDisposalMainSerializer(main).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = DailyTargetDisposalCreateSerializer(instance, data=request.data, partial=kwargs.get("partial", False))
        ser.is_valid(raise_exception=True)
        main = ser.save()
        return Response(DailyTargetDisposalMainSerializer(main).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AfrTransportRfqViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AfrTransportRfq.objects.filter(is_deleted=False)
    serializer_class = AfrTransportRfqSerializer
    filterset_class = AfrTransportRfqFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AggregateEntryViewSet(viewsets.ModelViewSet):
    """Aggregate Entry (legacy scrap_entry)."""
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AggregateEntryMain.objects.filter(is_deleted=False)
    filterset_class = AggregateEntryFilter
    lookup_field = "unique_id"

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return AggregateEntryCreateSerializer
        return AggregateEntryMainSerializer

    def create(self, request, *args, **kwargs):
        ser = AggregateEntryCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        main = ser.save(created_by=request.headers.get("X-Username", ""))
        return Response(AggregateEntryMainSerializer(main).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = AggregateEntryCreateSerializer(instance, data=request.data, partial=kwargs.get("partial", False))
        ser.is_valid(raise_exception=True)
        main = ser.save(updated_by=request.headers.get("X-Username", ""))
        return Response(AggregateEntryMainSerializer(main).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AfrTransportEntryViewSet(viewsets.ModelViewSet):
    """AFR Transport Entry (legacy trans_appr_entry)."""
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AfrTransportEntryMain.objects.filter(is_deleted=False).prefetch_related("sub_items")
    filterset_class = AfrTransportEntryFilter
    lookup_field = "unique_id"

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return AfrTransportEntryCreateSerializer
        return AfrTransportEntryMainSerializer

    def create(self, request, *args, **kwargs):
        ser = AfrTransportEntryCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        main = ser.save(created_by=request.headers.get("X-Username", ""))
        return Response(AfrTransportEntryMainSerializer(main).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = AfrTransportEntryCreateSerializer(instance, data=request.data, partial=kwargs.get("partial", False))
        ser.is_valid(raise_exception=True)
        main = ser.save(updated_by=request.headers.get("X-Username", ""))
        return Response(AfrTransportEntryMainSerializer(main).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================
# PHASE A VIEWSETS
# ============================================================

class IcwWorkOrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = IcwWorkOrder.objects.filter(is_deleted=False)
    serializer_class = IcwWorkOrderSerializer
    filterset_class = IcwWorkOrderFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NegativeInvoiceViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = NegativeInvoice.objects.filter(is_deleted=False)
    serializer_class = NegativeInvoiceSerializer
    filterset_class = NegativeInvoiceFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FreightLetterViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FreightLetter.objects.filter(is_deleted=False)
    serializer_class = FreightLetterSerializer
    filterset_class = FreightLetterFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CoProcessingViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CoProcessingCertificate.objects.filter(is_deleted=False)
    serializer_class = CoProcessingCertificateSerializer
    filterset_class = CoProcessingFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AggregateComparisonViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = AggregateComparison.objects.filter(is_deleted=False)
    serializer_class = AggregateComparisonSerializer
    filterset_class = AggregateComparisonFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScrapQuotationComparisonViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ScrapQuotationComparison.objects.filter(is_deleted=False)
    serializer_class = ScrapQuotationComparisonSerializer
    filterset_class = ScrapQuotationComparisonFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConfirmationReceiptViewSet(viewsets.ModelViewSet):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ConfirmationReceiptDc.objects.filter(is_deleted=False)
    serializer_class = ConfirmationReceiptDcSerializer
    filterset_class = ConfirmationReceiptFilter
    lookup_field = "unique_id"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.headers.get("X-Username", ""))

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.headers.get("X-Username", ""))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
