from apps.sales_shared.services.approval_service import BaseApprovalService
from apps.sales_transaction.models.work_order import WorkOrderMain


class WorkOrderApprovalService(BaseApprovalService):
    """
    4-level Work Order approval:
    1. DTC (Department) - work_order_dtc_appr_status
    2. GM (Asst.Associate) - work_order_appr_status
    3. Director - work_order_dt_appr_status
    4. Send - send_status
    """

    entity_type = "work_order"
    model = WorkOrderMain
    status_field = "work_order_dtc_appr_status"

    allowed_transitions = {
        "approve": [("0", "1"), ("*", "1")],
        "reject": [("0", "3"), ("1", "3"), ("*", "3")],
        "cancel": [("0", "3"), ("1", "3"), ("2", "3"), ("*", "3")],
        "hold": [("0", "2"), ("*", "2")],
    }

    def approve_dtc(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._perform_action_for_field(
            "work_order_dtc_appr_status", "work_order_dtc_approve_date",
            "work_order_dtc_dt_desc", "wo_app_dtid",
            entity_unique_id, approver_id, approver_name, remarks, site_id,
        )

    def approve_gm(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._perform_action_for_field(
            "work_order_appr_status", "work_order_appr_date",
            "work_order_appr_desc", "wo_app_gmid",
            entity_unique_id, approver_id, approver_name, remarks, site_id,
        )

    def approve_director(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._perform_action_for_field(
            "work_order_dt_appr_status", "work_order_dt_approve_date",
            "work_order_appr_dt_desc", "wo_app_dirid",
            entity_unique_id, approver_id, approver_name, remarks, site_id,
        )

    def send_work_order(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        from django.utils import timezone
        from django.db import transaction
        from apps.sales_shared.models.approval_status import ApprovalHistory

        with transaction.atomic():
            instance = WorkOrderMain.objects.select_for_update().get(
                unique_id=entity_unique_id, is_deleted=False,
            )
            previous_status = instance.send_status
            instance.send_status = "1"
            instance.wo_send_desc = remarks
            instance.wo_send_date = timezone.now()
            instance.wo_send_id = str(approver_id)
            instance.save(update_fields=[
                "send_status", "wo_send_desc", "wo_send_date", "wo_send_id", "updated_at",
            ])
            ApprovalHistory.objects.create(
                entity_type=self.entity_type,
                entity_id=instance.unique_id,
                action="send",
                previous_status=previous_status,
                new_status="1",
                approver_id=str(approver_id),
                approver_name=approver_name or "",
                remarks=remarks or "",
                site_id=site_id,
            )
            return instance

    def _perform_action_for_field(
        self, status_field, date_field, desc_field, approver_field,
        entity_unique_id, approver_id, approver_name, remarks, site_id,
    ):
        from django.utils import timezone
        from django.db import transaction
        from apps.sales_shared.models.approval_status import ApprovalHistory

        with transaction.atomic():
            instance = WorkOrderMain.objects.select_for_update().get(
                unique_id=entity_unique_id, is_deleted=False,
            )
            previous_status = getattr(instance, status_field)
            setattr(instance, status_field, "1")
            setattr(instance, date_field, timezone.now())
            setattr(instance, desc_field, remarks)
            setattr(instance, approver_field, str(approver_id))
            instance.save(update_fields=[
                status_field, date_field, desc_field, approver_field, "updated_at",
            ])
            ApprovalHistory.objects.create(
                entity_type=self.entity_type,
                entity_id=instance.unique_id,
                action="approve",
                previous_status=previous_status,
                new_status="1",
                approver_id=str(approver_id),
                approver_name=approver_name or "",
                remarks=remarks or "",
                site_id=site_id,
            )
            return instance

    def get_history(self, entity_unique_id):
        from apps.sales_shared.models.approval_status import ApprovalHistory
        return ApprovalHistory.objects.filter(
            entity_type=self.entity_type, entity_id=entity_unique_id,
        ).order_by("-created_at")
