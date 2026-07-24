import uuid
from django.db import models


class ReceivableEntry(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")

    invoice_no = models.CharField(max_length=50, unique=True)
    entry_date = models.DateField()

    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    supplier_name = models.CharField(max_length=255, blank=True, default="")

    tot_qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gst_amt = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tot_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_amt = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_amt = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    description = models.TextField(blank=True, default="")
    invoice_date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["invoice_no"]),
            models.Index(fields=["site_id"]),
            models.Index(fields=["entry_date"]),
        ]

    def __str__(self):
        return self.invoice_no

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class ReceivableEntrySub(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    receivable_entry = models.ForeignKey(ReceivableEntry, on_delete=models.CASCADE, related_name="sub_items")

    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")
    invoice_no = models.CharField(max_length=50, blank=True, default="")
    entry_date = models.DateField(null=True, blank=True)
    site_id = models.UUIDField(null=True, blank=True)
    supplier_name = models.CharField(max_length=255, blank=True, default="")
    invoice_date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)

    dc_no = models.CharField(max_length=50, blank=True, default="")
    qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_per = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        indexes = [models.Index(fields=["invoice_no"])]
