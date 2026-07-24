import uuid

from django.db import models


class ApprovalStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    DEPARTMENT_APPROVED = "department_approved", "Department Approved"
    ACCOUNTS_APPROVED = "accounts_approved", "Accounts Approved"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    RETURNED = "returned", "Returned for Correction"
    CANCELLED = "cancelled", "Cancelled"
    VERIFIED = "verified", "Verified"
    PENDING_VERIFICATION = "pending_verification", "Pending Verification"
    PENDING_CONFIRMATION = "pending_confirmation", "Pending Confirmation"
    CONFIRMED = "confirmed", "Confirmed"
    CLOSED = "closed", "Closed"
    ON_HOLD = "on_hold", "On Hold"
    SENT = "sent", "Sent"


class ApprovalHistory(models.Model):
    """
    Generic audit trail for all approval actions across the sales module.
    Tracks every status change with who, when, what, and remarks.
    """

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    entity_type = models.CharField(
        max_length=100,
        help_text="Type of entity, e.g. 'work_order', 'customer_creation', 'invoice'",
    )
    entity_id = models.UUIDField(
        help_text="unique_id of the entity being approved",
    )

    action = models.CharField(
        max_length=30,
        choices=[
            ("submit", "Submit"),
            ("approve", "Approve"),
            ("reject", "Reject"),
            ("cancel", "Cancel"),
            ("return", "Return for Correction"),
            ("verify", "Verify"),
            ("confirm", "Confirm"),
            ("send", "Send"),
            ("hold", "Hold"),
            ("resume", "Resume"),
        ],
    )

    previous_status = models.CharField(max_length=50, blank=True, default="")
    new_status = models.CharField(max_length=50, blank=True, default="")

    approver_id = models.CharField(max_length=40, help_text="User ID of the approver")
    approver_name = models.CharField(max_length=150, blank=True, default="")

    remarks = models.TextField(blank=True, default="")
    site_id = models.UUIDField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["entity_type", "entity_id", "created_at"]),
            models.Index(fields=["approver_id"]),
        ]

    def __str__(self):
        return (
            f"{self.entity_type}:{self.entity_id} | "
            f"{self.action} | {self.previous_status} -> {self.new_status}"
        )
