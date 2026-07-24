import uuid
from django.db import models


class NocDocument(models.Model):

    class ApproveStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVE = "Approve", "Approve"
        REJECT = "Reject", "Reject"
        CANCEL = "Cancel", "Cancel"

    class OverallStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVE = "Approve", "Approve"

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    scrap_customer_id = models.UUIDField(help_text="CustomerCreationMaster unique_id")
    scrap_item_purpose_id = models.UUIDField(null=True, blank=True, help_text="CustomerItemPurpose unique_id")
    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    noc_doc_type_id = models.UUIDField(
        null=True, blank=True, help_text="DocumentTypeMaster unique_id"
    )
    dispose_type = models.CharField(max_length=50, blank=True, default="")
    customer_destination = models.CharField(max_length=255, blank=True, default="")
    entry_date = models.DateField(null=True, blank=True)
    after_image_month = models.CharField(max_length=20, blank=True, default="")
    staff_id = models.CharField(max_length=40, blank=True, default="", help_text="Uploader staff id")

    document_name = models.CharField(max_length=255, blank=True, default="")
    document_file = models.FileField(upload_to="noc_documents/%Y/%m/", blank=True, null=True)

    approve_status = models.CharField(max_length=10, choices=ApproveStatus.choices, default=ApproveStatus.PENDING)
    approve_staff_id = models.CharField(max_length=40, blank=True, default="")
    approve_date = models.DateField(null=True, blank=True)
    reason = models.TextField(blank=True, default="")

    overall_approve_status = models.CharField(max_length=10, choices=OverallStatus.choices, default=OverallStatus.PENDING)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["scrap_customer_id"]),
            models.Index(fields=["site_id"]),
            models.Index(fields=["approve_status"]),
        ]

    def __str__(self):
        return f"NOC-{self.scrap_customer_id}"


class NocDocumentApprovalHistory(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    noc_document = models.ForeignKey(NocDocument, on_delete=models.CASCADE, related_name="approval_history")

    approve_date = models.DateField()
    approve_status = models.CharField(max_length=10)
    approve_staff_id = models.CharField(max_length=40)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
