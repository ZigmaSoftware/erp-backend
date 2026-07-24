import uuid
from django.db import models


class PayableEntryMain(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")

    payable_no = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    entry_date = models.DateField()
    time = models.TimeField(null=True, blank=True)

    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    supplier_name = models.CharField(max_length=255, blank=True, default="")

    tot_qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gst_amt = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tot_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payable_qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    payable_amt = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    description = models.TextField(blank=True, default="")
    dc_num = models.CharField(max_length=50, blank=True, default="")
    pay_no = models.CharField(max_length=50, blank=True, default="")
    payable_file = models.CharField(max_length=500, blank=True, default="")

    appr_status = models.CharField(max_length=20, blank=True, default="")
    appr_date = models.DateTimeField(null=True, blank=True)
    appr_by = models.CharField(max_length=40, blank=True, default="")

    add_user = models.CharField(max_length=40, blank=True, default="")
    edit_user = models.CharField(max_length=40, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payable_no"]),
            models.Index(fields=["site_id"]),
            models.Index(fields=["entry_date"]),
            models.Index(fields=["appr_status"]),
        ]

    def __str__(self):
        return self.payable_no

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class PayableEntrySub(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    payable_entry = models.ForeignKey(PayableEntryMain, on_delete=models.CASCADE, related_name="sub_items")

    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")
    payable_no = models.CharField(max_length=50, blank=True, default="")
    entry_date = models.DateField(null=True, blank=True)
    site_id = models.UUIDField(null=True, blank=True)
    supplier_name = models.CharField(max_length=255, blank=True, default="")

    invoice_no = models.CharField(max_length=50, blank=True, default="")
    qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_per = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amt = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    invoice_date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    freight_charges = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loading_charges = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pay_no = models.CharField(max_length=50, blank=True, default="")
    customer_qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        indexes = [models.Index(fields=["payable_no"])]
