from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema

from apps.sales_master.models.customer_destination import CustomerDestination
from apps.sales_master.models.customer_item_purpose import CustomerItemPurpose
from apps.sales_master.serializers.customer_item_purpose_serializer import (
    CustomerItemPurposeSerializer,
)
from apps.sales_transaction.models.noc_document import NocDocument
from shared.master_service import resolve_site_names


class CustomerItemPurposeViewSet(ModelViewSet):
    """
    Customer Item / Purpose API
    -----------------------------
    CRUD operations for CustomerItemPurpose (sub-list line items).
    """

    serializer_class = CustomerItemPurposeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "unique_id"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = (
            CustomerItemPurpose.objects.filter(is_deleted=False)
            .select_related("customer", "item")
        )
        customer = self.request.query_params.get("customer")
        if customer:
            queryset = queryset.filter(customer__unique_id=customer)
        return queryset

    @swagger_auto_schema(
        operation_summary="Create customer item/purpose",
        request_body=CustomerItemPurposeSerializer,
        responses={201: CustomerItemPurposeSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )
        if serializer.instance:
            serializer.instance.refresh_from_db()

    @swagger_auto_schema(
        operation_summary="Update customer item/purpose",
        request_body=CustomerItemPurposeSerializer,
        responses={200: CustomerItemPurposeSerializer},
    )
    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user.username
            if self.request.user.is_authenticated
            else None
        )

    def destroy(self, request, *args, **kwargs):
        item_purpose = self.get_object()
        item_purpose.is_deleted = True
        item_purpose.is_active = False
        item_purpose.updated_by = (
            request.user.username
            if request.user.is_authenticated
            else None
        )
        item_purpose.save(update_fields=["is_deleted", "is_active", "updated_by"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary="NOC upload worklist",
        operation_description=(
            "Item/purpose rows for customers with NOC upload enabled, joined "
            "with their matching active destination. Existing uploaded NOC "
            "documents are returned under each worklist row."
        ),
    )
    @action(detail=False, methods=["get"], url_path="noc-list")
    def noc_list(self, request):
        customer = request.query_params.get("customer")
        site = request.query_params.get("site")

        def noc_disposal_verify_status(noc_documents):
            statuses = {document.approve_status for document in noc_documents}
            if statuses & {
                NocDocument.ApproveStatus.REJECT,
                NocDocument.ApproveStatus.CANCEL,
            }:
                return "Cancel"
            if not statuses or NocDocument.ApproveStatus.PENDING in statuses:
                return "Pending"
            if statuses == {NocDocument.ApproveStatus.APPROVE}:
                return "Verified"
            return "Pending"

        queryset = (
            CustomerItemPurpose.objects.filter(
                is_deleted=False,
                status=CustomerItemPurpose.Status.ACTIVE,
                customer__is_deleted=False,
                customer__noc_upload=True,
            )
            .select_related("customer", "item")
        )
        if customer:
            queryset = queryset.filter(customer__unique_id=customer)
        if site:
            queryset = queryset.filter(site=site)

        customer_ids = {ip.customer_id for ip in queryset}
        active_destinations = {
            (d.customer_id, str(d.site), d.destination.strip().lower()): d
            for d in CustomerDestination.objects.filter(
                is_deleted=False,
                status=CustomerDestination.Status.ACTIVE,
                customer_id__in=customer_ids,
            )
        }

        site_ids = {str(ip.site) for ip in queryset}
        site_names = resolve_site_names(site_ids, request)

        rows = []
        for item_purpose in queryset:
            key = (
                item_purpose.customer_id,
                str(item_purpose.site),
                item_purpose.destination.strip().lower(),
            )
            destination = active_destinations.get(key)
            if destination is None:
                continue

            # NOC documents are created only after the user clicks Submit in
            # the upload dialog.  There can be more than one document for a
            # customer/item row, so return the uploaded records as a nested
            # list instead of manufacturing a single placeholder record.
            noc_documents = NocDocument.objects.filter(
                scrap_item_purpose_id=item_purpose.unique_id,
                is_deleted=False,
                document_file__isnull=False,
            ).exclude(document_file="")

            noc_documents = list(noc_documents)
            documents = [
                {
                    "unique_id": str(noc_document.unique_id),
                    "entry_date": (
                        noc_document.entry_date.isoformat()
                        if noc_document.entry_date
                        else item_purpose.customer.entry_date.isoformat()
                    ),
                    "noc_doc_type_id": (
                        str(noc_document.noc_doc_type_id)
                        if noc_document.noc_doc_type_id
                        else None
                    ),
                    "document_name": noc_document.document_name,
                    "document_file": (
                        request.build_absolute_uri(noc_document.document_file.url)
                        if noc_document.document_file
                        else None
                    ),
                    "approve_date": (
                        noc_document.approve_date.isoformat()
                        if noc_document.approve_date
                        else None
                    ),
                    "approve_status": noc_document.approve_status,
                }
                for noc_document in noc_documents
            ]

            rows.append(
                {
                    "unique_id": str(item_purpose.unique_id),
                    "item_purpose_id": str(item_purpose.unique_id),
                    "customer_id": str(item_purpose.customer.unique_id),
                    "customer_name": item_purpose.customer.customer_name,
                    "customer_entry_date": item_purpose.customer.entry_date.isoformat(),
                    "site_id": str(item_purpose.site),
                    "site_name": site_names.get(str(item_purpose.site), ""),
                    "destination": item_purpose.destination,
                    "item_name": item_purpose.item.item_name,
                    "disposal_type": item_purpose.disposal_type,
                    "item_verification_status": noc_disposal_verify_status(noc_documents),
                    "destination_verification_status": destination.verification_status,
                    "documents": documents,
                }
            )

        return Response(rows)
