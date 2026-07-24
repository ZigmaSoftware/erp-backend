import uuid
from django.db import models


class InvoiceGeneration(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")

    invoice_no = models.CharField(max_length=50, unique=True)
    dc_no = models.CharField(max_length=50, blank=True, default="")
    entry_date = models.DateField()

    customer_name = models.UUIDField(help_text="CustomerCreationMaster unique_id")

    tot_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_ton = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    term_of_payment = models.CharField(max_length=255, blank=True, default="")
    despatch_doc_no = models.CharField(max_length=100, blank=True, default="")
    supplier_ref = models.CharField(max_length=100, blank=True, default="")
    other_ref = models.CharField(max_length=100, blank=True, default="")
    term_of_delivery = models.CharField(max_length=255, blank=True, default="")
    buyer_order_no = models.CharField(max_length=100, blank=True, default="")

    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    round_off = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    freight = models.CharField(max_length=100, blank=True, default="")
    vehicle_capacity = models.CharField(max_length=100, blank=True, default="")
    freight_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    loading_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    advance_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    hidden_val = models.TextField(blank=True, default="")

    site_id = models.UUIDField(help_text="Master Service Site unique_id")

    invoice_type = models.CharField(max_length=20, choices=[
        ("Invoice", "Invoice (Receivable)"), ("Others", "Others (Payable/Negative)"),
    ], default="Invoice")
    type_of_cost = models.CharField(max_length=20, choices=[
        ("normal", "Normal"), ("negative", "Negative"),
    ], default="normal")

    coordinate_status = models.CharField(max_length=5, default="0")
    approve_date = models.DateTimeField(null=True, blank=True)
    approve_user = models.CharField(max_length=40, blank=True, default="")
    app_desc = models.TextField(blank=True, default="")
    payable_status = models.CharField(max_length=5, default="0")
    cr_date = models.DateTimeField(null=True, blank=True)

    add_user = models.CharField(max_length=40, blank=True, default="")
    edit_user = models.CharField(max_length=40, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["invoice_no"]),
            models.Index(fields=["dc_no"]),
            models.Index(fields=["site_id"]),
            models.Index(fields=["customer_name"]),
            models.Index(fields=["entry_date"]),
            models.Index(fields=["invoice_type"]),
            models.Index(fields=["coordinate_status"]),
        ]

    def __str__(self):
        return self.invoice_no

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class InvoiceSub(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    invoice = models.ForeignKey(InvoiceGeneration, on_delete=models.CASCADE, related_name="sub_items")

    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")
    invoice_no = models.CharField(max_length=50, blank=True, default="")
    entry_date = models.DateField(null=True, blank=True)
    customer_name = models.UUIDField(null=True, blank=True)
    dc_no = models.CharField(max_length=50, blank=True, default="")

    item_name = models.UUIDField(null=True, blank=True)
    hsn_code = models.CharField(max_length=20, blank=True, default="")
    qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    dc_sub_id = models.UUIDField(null=True, blank=True)
    invoice_type = models.CharField(max_length=20, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        indexes = [models.Index(fields=["invoice_no"])]

    def save(self, *args, **kwargs):
        self.amount = self.qty * self.rate
        super().save(*args, **kwargs)
