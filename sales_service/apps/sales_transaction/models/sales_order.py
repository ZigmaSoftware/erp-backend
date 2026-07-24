import uuid
from django.db import models


class SalesOrderStatus(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")

    wrk_ord_id = models.UUIDField(null=True, blank=True, help_text="WorkOrderMain unique_id")
    entry_date = models.DateField()
    invoice_no = models.CharField(max_length=50, blank=True, default="")
    work_no = models.CharField(max_length=50, blank=True, default="")

    customer_name = models.UUIDField(help_text="CustomerCreationMaster unique_id")
    item_name = models.UUIDField(help_text="ItemCreation unique_id")
    site_id = models.UUIDField(help_text="Master Service Site unique_id")

    target = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    per_ton_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gst_type = models.CharField(max_length=20, choices=[
        ("Receivable", "Receivable"), ("Payable", "Payable"),
    ], default="Receivable")

    approve_status = models.CharField(max_length=20, choices=[
        ("Pending", "Pending"), ("Approve", "Approve"), ("Cancel", "Cancel"),
    ], default="Pending")
    approve_date = models.DateTimeField(null=True, blank=True)
    approve_staff_id = models.CharField(max_length=40, blank=True, default="")
    reason = models.TextField(blank=True, default="")

    approve_status_dept = models.CharField(max_length=20, blank=True, default="")
    approve_date_dept = models.DateTimeField(null=True, blank=True)
    approve_dept_staff_id = models.CharField(max_length=40, blank=True, default="")
    dept_reason = models.TextField(blank=True, default="")

    approve_status_acc = models.CharField(max_length=20, blank=True, default="")
    approve_date_acc = models.DateTimeField(null=True, blank=True)
    approve_acc_staff_id = models.CharField(max_length=40, blank=True, default="")
    acc_reason = models.TextField(blank=True, default="")

    work_order_status = models.CharField(max_length=5, default="0")
    work_order_qty_exceeded = models.CharField(max_length=5, default="0")

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
            models.Index(fields=["customer_name"]),
            models.Index(fields=["approve_status"]),
        ]


class SalesOrderTransport(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sales_order = models.ForeignKey(SalesOrderStatus, on_delete=models.CASCADE, related_name="transports")

    work_no = models.CharField(max_length=50, blank=True, default="")
    transport_id = models.UUIDField(null=True, blank=True)
    entry_date = models.DateField(null=True, blank=True)
    transport_name = models.CharField(max_length=255, blank=True, default="")
    cost_type = models.CharField(max_length=20, choices=[
        ("Load Based", "Load Based"), ("Ton Based", "Ton Based"),
    ], default="Load Based")
    destination = models.CharField(max_length=255, blank=True, default="")
    cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=5, default="0")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
