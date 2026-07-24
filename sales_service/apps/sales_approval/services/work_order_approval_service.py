from django.utils import timezone

from apps.sales_shared.services.approval_service import BaseApprovalService
from apps.sales_transaction.models.work_order import WorkOrderMain


# Status constants
PENDING = "0"
APPROVED = "1"
HOLD = "2"
CANCEL = "3"


class WorkOrderApprovalService(BaseApprovalService):
    """
    4-level Work Order approval:
      Level 1: DTC Committee  -> work_order_dtc_appr_status
      Level 2: GM (Asst.Assoc) -> work_order_appr_status
      Level 3: Director        -> work_order_dt_appr_status
      Level 4: Send            -> send_status
    """
    entity_type = "work_order"
    model = WorkOrderMain

    _wo_transitions = {
        "approve": [(PENDING, APPROVED), (HOLD, APPROVED)],
        "reject": [(PENDING, CANCEL), (APPROVED, CANCEL)],
        "hold": [(PENDING, HOLD), (APPROVED, HOLD)],
        "cancel": [("*", CANCEL)],
    }

    # Level 1: DTC
    def dtc_approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._wo_transitions
        self.status_field = "work_order_dtc_appr_status"
        instance = self.approve(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.work_order_dtc_approve_date = timezone.now()
        instance.wo_app_dtid = str(approver_id)
        instance.work_order_dtc_dt_desc = remarks
        instance.save(update_fields=[
            "work_order_dtc_approve_date", "wo_app_dtid", "work_order_dtc_dt_desc",
        ])
        return instance

    def dtc_reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._wo_transitions
        self.status_field = "work_order_dtc_appr_status"
        instance = self.reject(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.work_order_dtc_approve_date = timezone.now()
        instance.wo_app_dtid = str(approver_id)
        instance.work_order_dtc_dt_desc = remarks
        instance.save(update_fields=[
            "work_order_dtc_approve_date", "wo_app_dtid", "work_order_dtc_dt_desc",
        ])
        return instance

    def dtc_hold(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._wo_transitions
        self.status_field = "work_order_dtc_appr_status"
        instance = self._perform_action("hold", entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.work_order_dtc_approve_date = timezone.now()
        instance.wo_app_dtid = str(approver_id)
        instance.work_order_dtc_dt_desc = remarks
        instance.save(update_fields=[
            "work_order_dtc_approve_date", "wo_app_dtid", "work_order_dtc_dt_desc",
        ])
        return instance

    # Level 2: GM
    def gm_approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._wo_transitions
        self.status_field = "work_order_appr_status"
        instance = self.approve(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.work_order_appr_date = timezone.now()
        instance.wo_app_gmid = str(approver_id)
        instance.work_order_appr_desc = remarks
        instance.save(update_fields=[
            "work_order_appr_date", "wo_app_gmid", "work_order_appr_desc",
        ])
        return instance

    def gm_reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._wo_transitions
        self.status_field = "work_order_appr_status"
        instance = self.reject(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.work_order_appr_date = timezone.now()
        instance.wo_app_gmid = str(approver_id)
        instance.work_order_appr_desc = remarks
        instance.save(update_fields=[
            "work_order_appr_date", "wo_app_gmid", "work_order_appr_desc",
        ])
        return instance

    # Level 3: Director
    def director_approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._wo_transitions
        self.status_field = "work_order_dt_appr_status"
        instance = self.approve(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.work_order_dt_approve_date = timezone.now()
        instance.wo_app_dirid = str(approver_id)
        instance.work_order_appr_dt_desc = remarks
        instance.save(update_fields=[
            "work_order_dt_approve_date", "wo_app_dirid", "work_order_appr_dt_desc",
        ])
        return instance

    def director_reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._wo_transitions
        self.status_field = "work_order_dt_appr_status"
        instance = self.reject(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.work_order_dt_approve_date = timezone.now()
        instance.wo_app_dirid = str(approver_id)
        instance.work_order_appr_dt_desc = remarks
        instance.save(update_fields=[
            "work_order_dt_approve_date", "wo_app_dirid", "work_order_appr_dt_desc",
        ])
        return instance

    # Level 4: Send
    _send_transitions = {
        "send": [(APPROVED, APPROVED)],
        "cancel": [("*", CANCEL)],
    }

    def send(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._send_transitions
        self.status_field = "send_status"
        instance = self._perform_action("send", entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.wo_send_date = timezone.now()
        instance.wo_send_id = str(approver_id)
        instance.wo_send_desc = remarks
        instance.save(update_fields=["wo_send_date", "wo_send_id", "wo_send_desc"])
        return instance
