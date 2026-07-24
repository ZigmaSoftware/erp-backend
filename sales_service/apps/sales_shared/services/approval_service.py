from django.db import transaction

from apps.sales_shared.models.approval_status import ApprovalHistory


class ApprovalError(Exception):
    pass


class BaseApprovalService:
    """
    Generic approval workflow service.
    Subclass for each entity type. Override entity_type, model, status_field,
    and allowed_transitions.
    """

    entity_type: str = ""
    model = None
    status_field: str = "status"
    allowed_transitions: dict[str, list[tuple[str, str]]] = {}

    def approve(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._perform_action("approve", entity_unique_id, approver_id, approver_name, remarks, site_id)

    def reject(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        if not remarks:
            raise ApprovalError("Rejection remarks are required.")
        return self._perform_action("reject", entity_unique_id, approver_id, approver_name, remarks, site_id)

    def cancel(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._perform_action("cancel", entity_unique_id, approver_id, approver_name, remarks, site_id)

    def submit(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        return self._perform_action("submit", entity_unique_id, approver_id, approver_name, remarks, site_id)

    def return_for_correction(self, entity_unique_id, approver_id, approver_name="", remarks="", site_id=None):
        if not remarks:
            raise ApprovalError("Return remarks are required.")
        return self._perform_action("return", entity_unique_id, approver_id, approver_name, remarks, site_id)

    def _perform_action(self, action, entity_unique_id, approver_id, approver_name, remarks, site_id):
        if not self.entity_type or not self.model:
            raise ApprovalError("entity_type and model must be set on the service class.")

        with transaction.atomic():
            instance = self.model.objects.select_for_update().get(
                unique_id=entity_unique_id, is_deleted=False,
            )
            current_status = getattr(instance, self.status_field, "")
            new_status = self._resolve_new_status(action, current_status)

            if new_status is None:
                raise ApprovalError(
                    f"Cannot '{action}' {self.entity_type} with status '{current_status}'."
                )

            setattr(instance, self.status_field, new_status)
            instance.save(update_fields=[self.status_field, "updated_at"])

            ApprovalHistory.objects.create(
                entity_type=self.entity_type,
                entity_id=instance.unique_id,
                action=action,
                previous_status=current_status,
                new_status=new_status,
                approver_id=str(approver_id),
                approver_name=approver_name or "",
                remarks=remarks or "",
                site_id=site_id,
            )
            return instance

    def _resolve_new_status(self, action, current_status):
        for from_status, to_status in self.allowed_transitions.get(action, []):
            if from_status == "*" or from_status == current_status:
                return to_status
        return None

    def get_history(self, entity_unique_id):
        return ApprovalHistory.objects.filter(
            entity_type=self.entity_type, entity_id=entity_unique_id,
        ).order_by("-created_at")
