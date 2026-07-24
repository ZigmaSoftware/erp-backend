from django.db import transaction
from django.utils import timezone

from apps.sales_shared.models.approval_status import ApprovalHistory
from apps.sales_transaction.models.freight_creation import FreightCreation


class FreightApprovalService:
    entity_type = "freight"

    def approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._do_status_change(entity_unique_id, "1", approver_id, approver_name, remarks, site_id)

    def reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        if not remarks:
            raise ValueError("Rejection remarks are required.")
        return self._do_status_change(entity_unique_id, "2", approver_id, approver_name, remarks, site_id)

    def _do_status_change(self, entity_unique_id, new_status, approver_id, approver_name, remarks, site_id):
        with transaction.atomic():
            instance = FreightCreation.objects.select_for_update().get(
                unique_id=entity_unique_id, is_deleted=False,
            )
            previous_status = instance.coordinate_status
            instance.coordinate_status = new_status
            instance.approve_date = timezone.now()
            instance.approve_user = str(approver_id)
            instance.app_desc = remarks
            instance.save(update_fields=[
                "coordinate_status", "approve_date", "approve_user", "app_desc", "updated_at",
            ])
            ApprovalHistory.objects.create(
                entity_type=self.entity_type,
                entity_id=instance.unique_id,
                action="approve" if new_status == "1" else "reject",
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
