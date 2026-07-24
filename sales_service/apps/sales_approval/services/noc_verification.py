from django.db import transaction
from django.utils import timezone

from apps.sales_transaction.models.noc_document import NocDocument, NocDocumentApprovalHistory


class NocVerificationService:
    entity_type = "noc_document"

    def approve(self, noc_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._perform_action(noc_unique_id, approver_id, approver_name, "Approve")

    def reject(self, noc_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._perform_action(noc_unique_id, approver_id, approver_name, "Reject")

    def _perform_action(self, noc_unique_id, approver_id, approver_name, action_status):
        with transaction.atomic():
            noc = NocDocument.objects.select_for_update().get(
                unique_id=noc_unique_id, is_deleted=False,
            )
            noc.approve_status = action_status
            noc.approve_staff_id = str(approver_id)
            noc.approve_date = timezone.now().date()
            noc.save(update_fields=[
                "approve_status", "approve_staff_id", "approve_date", "updated_at",
            ])

            NocDocumentApprovalHistory.objects.create(
                noc_document=noc,
                approve_date=timezone.now().date(),
                approve_status=action_status,
                approve_staff_id=str(approver_id),
            )

            if action_status == "Approve":
                self._check_and_set_overall_status(noc)

            return noc

    def _check_and_set_overall_status(self, noc):
        mandatory_docs = NocDocument.objects.filter(
            scrap_customer_id=noc.scrap_customer_id,
            site_id=noc.site_id,
            dispose_type=noc.dispose_type,
            customer_destination=noc.customer_destination,
            is_deleted=False,
        )
        all_approved = mandatory_docs.exclude(approve_status="Approve").count() == 0
        if all_approved and mandatory_docs.exists():
            noc.overall_approve_status = "Approve"
            noc.save(update_fields=["overall_approve_status", "updated_at"])

    def get_history(self, noc_unique_id):
        return NocDocumentApprovalHistory.objects.filter(
            noc_document__unique_id=noc_unique_id,
        ).order_by("-created_at")
