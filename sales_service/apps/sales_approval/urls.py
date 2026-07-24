from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.sales_approval.views import WorkOrderApprovalViewSet
from apps.sales_approval.views.approval_viewsets import (
    CustomerApprovalViewSet,
    SalesOrderApprovalViewSet,
    FreightApprovalViewSet,
    InvoiceApprovalViewSet,
    PayableApprovalViewSet,
    AfrTransportApprovalViewSet,
    ReceivableApprovalViewSet,
    NocVerificationViewSet,
)

router = DefaultRouter()
router.register(r"work-orders", WorkOrderApprovalViewSet, basename="wo-approval")
router.register(r"customers", CustomerApprovalViewSet, basename="customer-approval")
router.register(r"sales-orders", SalesOrderApprovalViewSet, basename="so-approval")
router.register(r"freights", FreightApprovalViewSet, basename="freight-approval")
router.register(r"invoices", InvoiceApprovalViewSet, basename="invoice-approval")
router.register(r"payables", PayableApprovalViewSet, basename="payable-approval")
router.register(r"afr-transports", AfrTransportApprovalViewSet, basename="afr-approval")
router.register(r"receivables", ReceivableApprovalViewSet, basename="receivable-approval")
router.register(r"noc-documents", NocVerificationViewSet, basename="noc-verification")

urlpatterns = [
    path("approvals/", include(router.urls)),
]
