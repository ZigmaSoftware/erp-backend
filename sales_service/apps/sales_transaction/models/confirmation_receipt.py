import uuid
from django.db import models


class ConfirmationReceiptDc(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    serial_number = models.CharField(max_length=100, unique=True)
    month_year = models.CharField(max_length=20)
    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    scrap_customer_id = models.UUIDField(help_text="CustomerCreationMaster unique_id")

    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    entry_date = models.DateField()

    approve_status = models.CharField(max_length=10, default="Pending")
    approve_user = models.CharField(max_length=40, blank=True, default="")
    approve_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["serial_number"]),
            models.Index(fields=["site_id"]),
            models.Index(fields=["entry_date"]),
        ]

    def __str__(self):
        return self.serial_number

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.images.all().update(is_deleted=True, is_active=False)


class ConfirmationReceiptImage(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    cor = models.ForeignKey(ConfirmationReceiptDc, on_delete=models.CASCADE, related_name="images")

    image_name = models.CharField(max_length=255)
    image_file = models.FileField(upload_to="cor_uploads/%Y/%m/")
    entry_date = models.DateField()
    entry_user = models.CharField(max_length=40, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
