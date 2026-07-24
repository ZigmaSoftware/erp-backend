from django.db import transaction
from django.utils import timezone

from apps.sales_shared.models.approval_status import ApprovalHistory
from apps.sales_transaction.models.payable_entry import PayableEntryMain


class PayableApprovalService:
    entity_type = "payable"

    def approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        with transaction.atomic():
            instance = PayableEntryMain.objects.select_for_update().get(
                unique_id=entity_unique_id, is_deleted=False,
            )
            previous_status = instance.appr_status
            instance.appr_status = "Approved"
            instance.appr_date = timezone.now()
            instance.appr_by = str(approver_id)
            instance.save(update_fields=["appr_status", "appr_date", "appr_by", "updated_at"])

            ApprovalHistory.objects.create(
                entity_type=self.entity_type,
                entity_id=instance.unique_id,
                action="approve",
                previous_status=previous_status,
                new_status="Approved",
                approver_id=str(approver_id),
                approver_name=approver_name or "",
                remarks=remarks or "",
                site_id=site_id,
            )
            return instance

    def reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        if not remarks:
            raise ValueError("Rejection remarks are required.")
        with transaction.atomic():
            instance = PayableEntryMain.objects.select_for_update().get(
                unique_id=entity_unique_id, is_deleted=False,
            )
            previous_status = instance.appr_status
            instance.appr_status = "Rejected"
            instance.appr_date = timezone.now()
            instance.appr_by = str(approver_id)
            instance.save(update_fields=["appr_status", "appr_date", "appr_by", "updated_at"])

            ApprovalHistory.objects.create(
                entity_type=self.entity_type,
                entity_id=instance.unique_id,
                action="reject",
                previous_status=previous_status,
                new_status="Rejected",
                approver_id=str(approver_id),
                approver_name=approver_name or "",
                remarks=remarks or "",
                site_id=site_id,
            )
            return instance

    def get_history(self, entity_unique_id):
        return ApprovalHistory.objects.filter(
            entity_type=self.entity_type, entity_id=entity_unique_id,
        ).order_by("-created_at")
