from django.db import transaction
from django.utils import timezone

from apps.sales_shared.models.approval_status import ApprovalHistory
from apps.sales_transaction.models.sales_order import SalesOrderStatus


class SalesOrderApprovalService:
    """
    3-level Sales Order approval:
    1. Site Level - approve_status
    2. Department Level - approve_status_dept
    3. Accounts Level - approve_status_acc
    """

    entity_type = "sales_order"

    def approve_site(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._do_approval(
            entity_unique_id, "approve_site", "approve_status",
            "approve_date", "approve_staff_id",
            approver_id, approver_name, remarks, site_id,
        )

    def approve_dept(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._do_approval(
            entity_unique_id, "approve_dept", "approve_status_dept",
            "approve_date_dept", "approve_dept_staff_id",
            approver_id, approver_name, remarks, site_id,
        )

    def approve_accounts(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._do_approval(
            entity_unique_id, "approve_acc", "approve_status_acc",
            "approve_date_acc", "approve_acc_staff_id",
            approver_id, approver_name, remarks, site_id,
        )

    def reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        if not remarks:
            raise ValueError("Rejection remarks are required.")
        return self._do_approval(
            entity_unique_id, "reject", "approve_status",
            "approve_date", "approve_staff_id",
            approver_id, approver_name, remarks, site_id,
        )

    def _do_approval(
        self, entity_unique_id, action, status_field, date_field, approver_field,
        approver_id, approver_name, remarks, site_id,
    ):
        with transaction.atomic():
            instance = SalesOrderStatus.objects.select_for_update().get(
                unique_id=entity_unique_id, is_deleted=False,
            )
            previous_status = getattr(instance, status_field, "") or ""
            new_status = "Approve" if "approve" in action else "Cancel"

            setattr(instance, status_field, new_status)
            setattr(instance, date_field, timezone.now())
            setattr(instance, approver_field, str(approver_id))
            instance.save(update_fields=[status_field, date_field, approver_field, "updated_at"])

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
