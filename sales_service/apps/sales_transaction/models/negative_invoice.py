import uuid
from django.db import models


class NegativeInvoice(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    invoice_no = models.CharField(max_length=50, unique=True)
    dc_no = models.CharField(max_length=50, blank=True, default="")
    entry_date = models.DateField()
    customer_name = models.UUIDField(help_text="CustomerCreationMaster unique_id")
    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    work_order_no = models.CharField(max_length=50, blank=True, default="")
    invoice_type = models.CharField(max_length=20, default="negative")
    description = models.TextField(blank=True, default="")

    tot_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    round_off = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    freight = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    advance_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    status = models.CharField(max_length=20, default="Pending")

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


class NegativeInvoiceSub(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    invoice = models.ForeignKey(NegativeInvoice, on_delete=models.CASCADE, related_name="sub_items")

    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_per = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        self.amount = self.qty * self.rate
        self.tax_amount = (self.amount / 100) * self.tax_per if self.tax_per else 0
        super().save(*args, **kwargs)
