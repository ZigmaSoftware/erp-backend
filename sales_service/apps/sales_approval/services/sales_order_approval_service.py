from django.utils import timezone

from apps.sales_shared.services.approval_service import BaseApprovalService
from apps.sales_transaction.models.sales_order import SalesOrderStatus


class SalesOrderApprovalService(BaseApprovalService):
    """
    3-level Sales Order approval:
      Level 1: Site        -> approve_status
      Level 2: Department  -> approve_status_dept
      Level 3: Accounts    -> approve_status_acc
    """
    entity_type = "sales_order"
    model = SalesOrderStatus

    _so_transitions = {
        "approve": [("Pending", "Approve")],
        "reject": [("Pending", "Cancel"), ("Approve", "Cancel")],
        "cancel": [("*", "Cancel")],
    }

    def site_approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._so_transitions
        self.status_field = "approve_status"
        instance = self.approve(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date = timezone.now()
        instance.approve_staff_id = str(approver_id)
        instance.reason = remarks
        instance.save(update_fields=["approve_date", "approve_staff_id", "reason"])
        return instance

    def site_reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._so_transitions
        self.status_field = "approve_status"
        instance = self.reject(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date = timezone.now()
        instance.approve_staff_id = str(approver_id)
        instance.reason = remarks
        instance.save(update_fields=["approve_date", "approve_staff_id", "reason"])
        return instance

    def dept_approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._so_transitions
        self.status_field = "approve_status_dept"
        instance = self.approve(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date_dept = timezone.now()
        instance.approve_dept_staff_id = str(approver_id)
        instance.dept_reason = remarks
        instance.save(update_fields=["approve_date_dept", "approve_dept_staff_id", "dept_reason"])
        return instance

    def dept_reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._so_transitions
        self.status_field = "approve_status_dept"
        instance = self.reject(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date_dept = timezone.now()
        instance.approve_dept_staff_id = str(approver_id)
        instance.dept_reason = remarks
        instance.save(update_fields=["approve_date_dept", "approve_dept_staff_id", "dept_reason"])
        return instance

    def acc_approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._so_transitions
        self.status_field = "approve_status_acc"
        instance = self.approve(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date_acc = timezone.now()
        instance.approve_acc_staff_id = str(approver_id)
        instance.acc_reason = remarks
        instance.save(update_fields=["approve_date_acc", "approve_acc_staff_id", "acc_reason"])
        return instance

    def acc_reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self._so_transitions
        self.status_field = "approve_status_acc"
        instance = self.reject(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date_acc = timezone.now()
        instance.approve_acc_staff_id = str(approver_id)
        instance.acc_reason = remarks
        instance.save(update_fields=["approve_date_acc", "approve_acc_staff_id", "acc_reason"])
        return instance
