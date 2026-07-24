from django.db import transaction
from django.utils import timezone

from apps.sales_shared.models.approval_status import ApprovalHistory
from apps.sales_transaction.models.receivable_entry import ReceivableEntry


class ReceivableApprovalService:
    entity_type = "receivable"
    model = ReceivableEntry
    status_field = "appr_status"

    def approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._perform_action("1", "approve", entity_unique_id, approver_id, approver_name, remarks, site_id)

    def reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._perform_action("2", "reject", entity_unique_id, approver_id, approver_name, remarks, site_id)

    def _perform_action(self, new_status, action, entity_unique_id, approver_id, approver_name, remarks, site_id):
        with transaction.atomic():
            instance = ReceivableEntry.objects.select_for_update().get(
                unique_id=entity_unique_id, is_deleted=False,
            )
            previous_status = instance.appr_status
            instance.appr_status = new_status
            instance.save(update_fields=["appr_status", "updated_at"])

            ApprovalHistory.objects.create(
                entity_type=self.entity_type,
                entity_id=instance.unique_id,
                action=action,
                previous_status=previous_status,
                new_status=new_status,
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
