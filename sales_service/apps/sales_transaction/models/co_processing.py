import uuid
from django.db import models
from decimal import Decimal


class CoProcessingCertificate(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")
    cpcr_no = models.CharField(max_length=50, unique=True, blank=True, default="")
    cpc_no = models.CharField(max_length=50, blank=True, default="")
    cpc_month = models.CharField(max_length=20, blank=True, default="")
    entry_date = models.DateField()
    customer_name = models.UUIDField(help_text="CustomerCreationMaster unique_id")
    site_name = models.UUIDField(null=True, blank=True, help_text="Site unique_id")
    prev_diff = models.DecimalField(max_digits=15, decimal_places=3, default=Decimal('0'))
    total_disp_qty = models.DecimalField(max_digits=15, decimal_places=3, default=Decimal('0'))
    total_received_qty = models.DecimalField(max_digits=15, decimal_places=3, default=Decimal('0'))
    diff = models.DecimalField(max_digits=15, decimal_places=3, default=Decimal('0'))
    remarks = models.TextField(blank=True, default="")
    certificate_upload = models.FileField(upload_to="co_processing/%Y/%m/", blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["cpcr_no"]),
            models.Index(fields=["customer_name"]),
            models.Index(fields=["site_name"]),
            models.Index(fields=["entry_date"]),
        ]

    def __str__(self):
        return self.cpcr_no or str(self.unique_id)

    def save(self, *args, **kwargs):
        self.diff = self.total_disp_qty - self.total_received_qty
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
