import uuid
from decimal import Decimal

from django.db import models


class AfrTransportEntryMain(models.Model):
    """
    Legacy: trans_appr_entry / trans_appr_entry_sublist ("AFR Transport Entry").
    Document number: ZEP-{site_head}-{YYYYMM}-NNNN (per-site, calendar-year reset).
    """

    class ApprovalStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=40, blank=True, default="")
    trans_appr_no = models.CharField(max_length=60, unique=True)

    entry_date = models.DateField()
    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    customer_id = models.UUIDField(null=True, blank=True, help_text="CustomerCreationMaster unique_id")
    customer_name = models.CharField(max_length=255, blank=True, default="")
    transporter_id = models.UUIDField(null=True, blank=True, help_text="Transport master unique_id")
    transporter_name = models.CharField(max_length=255, blank=True, default="")
    cpcr_no = models.CharField(max_length=100, blank=True, default="")
    remarks = models.TextField(blank=True, default="")

    approval_status = models.CharField(
        max_length=15, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING
    )
    approval_date = models.DateField(null=True, blank=True)
    approval_by = models.CharField(max_length=40, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["trans_appr_no"]),
            models.Index(fields=["site_id"]),
            models.Index(fields=["entry_date"]),
            models.Index(fields=["approval_status"]),
        ]

    def __str__(self):
        return self.trans_appr_no

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class AfrTransportEntrySub(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    main = models.ForeignKey(AfrTransportEntryMain, on_delete=models.CASCADE, related_name="sub_items")

    material_type = models.CharField(max_length=100, blank=True, default="")
    freight_basis = models.CharField(max_length=100, blank=True, default="")
    freight_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_type = models.CharField(max_length=50, blank=True, default="")
    tax_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    tax_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_freight_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cus_po_val = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    po_tax = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    po_tax_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_po_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_cost_per_ton = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        # Derived server-side to mirror legacy trans_appr_entry.js:182-206 and to
        # avoid trusting client-supplied totals.
        hundred = Decimal("100")
        freight = self.freight_cost or Decimal("0")
        po_val = self.cus_po_val or Decimal("0")
        self.tax_value = (freight * (self.tax_percentage or 0)) / hundred
        self.total_freight_cost = freight + self.tax_value
        self.po_tax_value = (po_val * (self.po_tax or 0)) / hundred
        self.total_po_value = po_val + self.po_tax_value
        self.net_cost_per_ton = self.total_po_value - self.total_freight_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.material_type} - {self.net_cost_per_ton}"
