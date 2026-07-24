import uuid
from django.db import models


class IcwWorkOrder(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    invoice_no = models.CharField(max_length=50, unique=True)
    entry_date = models.DateField()
    customer_name = models.UUIDField(help_text="CustomerCreationMaster unique_id")
    item_name = models.CharField(max_length=255)
    target = models.DecimalField(max_digits=15, decimal_places=3)
    start_date = models.DateField()
    end_date = models.DateField()
    per_ton_cost = models.DecimalField(max_digits=15, decimal_places=2)
    gst_type = models.CharField(max_length=20, blank=True, default="")
    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    state_id = models.UUIDField(null=True, blank=True)
    category_id = models.UUIDField(null=True, blank=True)
    group_id = models.UUIDField(null=True, blank=True)
    work_no = models.CharField(max_length=50, blank=True, default="")
    work_order_status = models.CharField(max_length=5, default="0")
    work_order_qty_exceeded = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    description = models.TextField(blank=True, default="")
    approve_status = models.CharField(max_length=10, default="Pending")
    mail_status = models.CharField(max_length=5, default="0")
    sales_work_order = models.CharField(max_length=50, blank=True, default="")

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
        self.transports.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class IcwWorkOrderTransport(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    work_order = models.ForeignKey(IcwWorkOrder, on_delete=models.CASCADE, related_name="transports")

    transport_name = models.CharField(max_length=255)
    transport_order_no = models.CharField(max_length=50)
    transport_qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
