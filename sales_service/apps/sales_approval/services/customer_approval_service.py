from django.utils import timezone

from apps.sales_shared.services.approval_service import BaseApprovalService
from apps.sales_master.models.customer_creation_master import CustomerCreationMaster


class CustomerApprovalService(BaseApprovalService):
    """
    3-level customer creation approval:
      Level 1: Site Manager  -> approve_status
      Level 2: Department    -> approve_status_dept
      Level 3: Accounts      -> approve_status_acc
    """
    entity_type = "customer_creation"
    model = CustomerCreationMaster
    status_field = "approve_status"

    # Level 1: Site approval
    site_approve_transitions = {
        "approve": [("", "Approve"), ("Pending", "Approve")],
        "reject": [("", "Cancel"), ("Pending", "Cancel")],
        "cancel": [("", "Cancel"), ("Approve", "Cancel")],
    }

    def site_approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self.site_approve_transitions
        self.status_field = "approve_status"
        instance = self.approve(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date = timezone.now()
        instance.approve_staff_id = str(approver_id)
        if remarks:
            instance.reject_reason = remarks
        instance.save(update_fields=["approve_date", "approve_staff_id", "reject_reason"])
        return instance

    def site_reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self.site_approve_transitions
        self.status_field = "approve_status"
        instance = self.reject(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date = timezone.now()
        instance.approve_staff_id = str(approver_id)
        instance.reject_reason = remarks
        instance.save(update_fields=["approve_date", "approve_staff_id", "reject_reason"])
        return instance

    # Level 2: Department approval
    dept_approve_transitions = {
        "approve": [("", "Approve"), ("Pending", "Approve")],
        "reject": [("", "Cancel"), ("Pending", "Cancel")],
        "cancel": [("", "Cancel"), ("Approve", "Cancel")],
    }

    def dept_approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self.dept_approve_transitions
        self.status_field = "approve_status_dept"
        instance = self.approve(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date_dept = timezone.now()
        instance.approve_dept_staff_id = str(approver_id)
        if remarks:
            instance.dept_reason = remarks
        instance.save(update_fields=["approve_date_dept", "approve_dept_staff_id", "dept_reason"])
        return instance

    def dept_reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self.dept_approve_transitions
        self.status_field = "approve_status_dept"
        instance = self.reject(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date_dept = timezone.now()
        instance.approve_dept_staff_id = str(approver_id)
        instance.dept_reason = remarks
        instance.save(update_fields=["approve_date_dept", "approve_dept_staff_id", "dept_reason"])
        return instance

    # Level 3: Accounts approval
    acc_approve_transitions = {
        "approve": [("", "Approve"), ("Pending", "Approve")],
        "reject": [("", "Cancel"), ("Pending", "Cancel")],
        "cancel": [("", "Cancel"), ("Approve", "Cancel")],
    }

    def acc_approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self.acc_approve_transitions
        self.status_field = "approve_status_acc"
        instance = self.approve(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date_acc = timezone.now()
        instance.approve_acc_staff_id = str(approver_id)
        if remarks:
            instance.acc_reason = remarks
        instance.save(update_fields=["approve_date_acc", "approve_acc_staff_id", "acc_reason"])
        return instance

    def acc_reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        self.allowed_transitions = self.acc_approve_transitions
        self.status_field = "approve_status_acc"
        instance = self.reject(entity_unique_id, approver_id, approver_name, remarks, site_id)
        instance.approve_date_acc = timezone.now()
        instance.approve_acc_staff_id = str(approver_id)
        instance.acc_reason = remarks
        instance.save(update_fields=["approve_date_acc", "approve_acc_staff_id", "acc_reason"])
        return instance
