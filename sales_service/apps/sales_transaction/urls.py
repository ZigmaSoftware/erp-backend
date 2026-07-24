from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.sales_transaction.views import (
    WorkOrderViewSet, SalesOrderViewSet, FreightViewSet,
    DcEntryViewSet, InvoiceViewSet, PayableViewSet, ReceivableViewSet,
    AggregateQuotationViewSet, ScrapQuotationViewSet, NocDocumentViewSet,
    DailyTargetDisposalViewSet, AfrTransportRfqViewSet,
    AggregateEntryViewSet, AfrTransportEntryViewSet,
    IcwWorkOrderViewSet, NegativeInvoiceViewSet, FreightLetterViewSet,
    CoProcessingViewSet, AggregateComparisonViewSet,
    ScrapQuotationComparisonViewSet, ConfirmationReceiptViewSet,
)
from apps.sales_transaction.views.reports import (
    SupplyChainReportView,
    AggregateStockReportView,
    AggregateStockPerDayReportView,
    GraphicalRepresentationView,
    SiteWiseDisposalReportView,
    SiteWiseDisposalComparisonView,
    ConsolidatedMonthlySiteWiseReportView,
    PayableReceivableTrackerView,
    CustomerCreationReportView,
    ConfirmationReceiptReportView,
    WorkOrderStatusReportView,
    MBSReportView,
    RDFTrackerReportView,
    ICWDetailsReportView,
    OthersAggregateComparisonReportView,
)

router = DefaultRouter()
router.register(r"work-orders", WorkOrderViewSet, basename="work-order")
router.register(r"sales-orders", SalesOrderViewSet, basename="sales-order")
router.register(r"freights", FreightViewSet, basename="freight")
router.register(r"dc-entries", DcEntryViewSet, basename="dc-entry")
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"payables", PayableViewSet, basename="payable")
router.register(r"receivables", ReceivableViewSet, basename="receivable")
router.register(r"aggregate-quotations", AggregateQuotationViewSet, basename="aggregate-quotation")
router.register(r"scrap-quotations", ScrapQuotationViewSet, basename="scrap-quotation")
router.register(r"noc-documents", NocDocumentViewSet, basename="noc-document")
router.register(r"daily-targets", DailyTargetDisposalViewSet, basename="daily-target")
router.register(r"afr-rfqs", AfrTransportRfqViewSet, basename="afr-rfq")
router.register(r"aggregate-entries", AggregateEntryViewSet, basename="aggregate-entry")
router.register(r"afr-transport-entries", AfrTransportEntryViewSet, basename="afr-transport-entry")
router.register(r"icw-work-orders", IcwWorkOrderViewSet, basename="icw-work-order")
router.register(r"negative-invoices", NegativeInvoiceViewSet, basename="negative-invoice")
router.register(r"freight-letters", FreightLetterViewSet, basename="freight-letter")
router.register(r"co-processing", CoProcessingViewSet, basename="co-processing")
router.register(r"aggregate-comparisons", AggregateComparisonViewSet, basename="aggregate-comparison")
router.register(r"scrap-comparisons", ScrapQuotationComparisonViewSet, basename="scrap-comparison")
router.register(r"confirmation-receipts", ConfirmationReceiptViewSet, basename="confirmation-receipt")

urlpatterns = [
    path("", include(router.urls)),
    path("reports/supply-chain/", SupplyChainReportView.as_view(), name="report-supply-chain"),
    path("reports/aggregate-stock/", AggregateStockReportView.as_view(), name="report-aggregate-stock"),
    path("reports/aggregate-stock-per-day/", AggregateStockPerDayReportView.as_view(), name="report-aggregate-stock-per-day"),
    path("reports/graphical/", GraphicalRepresentationView.as_view(), name="report-graphical"),
    path("reports/site-wise-disposal/", SiteWiseDisposalReportView.as_view(), name="report-site-wise-disposal"),
    path("reports/site-wise-disposal-comparison/", SiteWiseDisposalComparisonView.as_view(), name="report-site-wise-disposal-comparison"),
    path("reports/consolidated-monthly/", ConsolidatedMonthlySiteWiseReportView.as_view(), name="report-consolidated-monthly"),
    path("reports/payable-receivable-tracker/", PayableReceivableTrackerView.as_view(), name="report-payable-receivable-tracker"),
    path("reports/customer-creation/", CustomerCreationReportView.as_view(), name="report-customer-creation"),
    path("reports/confirmation-receipt/", ConfirmationReceiptReportView.as_view(), name="report-confirmation-receipt"),
    path("reports/work-order-status/", WorkOrderStatusReportView.as_view(), name="report-work-order-status"),
    path("reports/mbs/", MBSReportView.as_view(), name="report-mbs"),
    path("reports/rdf-tracker/", RDFTrackerReportView.as_view(), name="report-rdf-tracker"),
    path("reports/icw-details/", ICWDetailsReportView.as_view(), name="report-icw-details"),
    path("reports/others-aggregate-comparison/", OthersAggregateComparisonReportView.as_view(), name="report-others-aggregate-comparison"),
]
