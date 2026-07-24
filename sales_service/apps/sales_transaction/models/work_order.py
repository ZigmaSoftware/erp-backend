import uuid
from django.db import models


class WorkOrderMain(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")
    workorderno = models.CharField(max_length=50, unique=True)

    suppliername = models.CharField(max_length=255)
    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    plant_name = models.CharField(max_length=150, blank=True, default="")
    department_name = models.CharField(max_length=150, blank=True, default="")

    description = models.TextField(blank=True, default="")
    entry_date = models.DateField()
    work_type = models.CharField(max_length=150, blank=True, default="")

    tot_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_amt = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tot_qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)

    payment_terms = models.CharField(max_length=255, blank=True, default="")
    comp_period = models.CharField(max_length=150, blank=True, default="")
    tds = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    package_forward = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    transport_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    freight_charge = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    budget_no = models.CharField(max_length=50, blank=True, default="")
    budget_entry_no = models.CharField(max_length=50, blank=True, default="")
    budget_po_type = models.CharField(max_length=50, blank=True, default="")

    # Approval: 0=Pending, 1=Approved, 2=Hold, 3=Cancel
    work_order_dtc_appr_status = models.CharField(max_length=5, default="0")
    work_order_dtc_approve_date = models.DateTimeField(null=True, blank=True)
    work_order_dtc_dt_desc = models.TextField(blank=True, default="")
    wo_app_dtid = models.CharField(max_length=40, blank=True, default="")

    work_order_appr_status = models.CharField(max_length=5, default="0")
    work_order_appr_date = models.DateTimeField(null=True, blank=True)
    work_order_appr_desc = models.TextField(blank=True, default="")
    wo_app_gmid = models.CharField(max_length=40, blank=True, default="")

    work_order_dt_appr_status = models.CharField(max_length=5, default="0")
    work_order_dt_approve_date = models.DateTimeField(null=True, blank=True)
    work_order_appr_dt_desc = models.TextField(blank=True, default="")
    wo_app_dirid = models.CharField(max_length=40, blank=True, default="")

    # Send
    send_status = models.CharField(max_length=5, default="0")
    wo_send_desc = models.TextField(blank=True, default="")
    wo_send_date = models.DateTimeField(null=True, blank=True)
    wo_send_id = models.CharField(max_length=40, blank=True, default="")

    # Work/Payment
    work_status = models.CharField(max_length=5, default="0")
    work_status_amnt = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_status = models.CharField(max_length=5, default="0")

    staff_id = models.CharField(max_length=40, blank=True, default="")
    ipaddress = models.CharField(max_length=45, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workorderno"]),
            models.Index(fields=["site_id"]),
            models.Index(fields=["entry_date"]),
            models.Index(fields=["work_order_dtc_appr_status"]),
            models.Index(fields=["work_order_appr_status"]),
            models.Index(fields=["work_order_dt_appr_status"]),
        ]

    def __str__(self):
        return self.workorderno

    def reset_approvals(self):
        self.work_order_dtc_appr_status = "0"
        self.work_order_appr_status = "0"
        self.work_order_dt_appr_status = "0"
        self.save(update_fields=[
            "work_order_dtc_appr_status", "work_order_appr_status",
            "work_order_dt_appr_status", "updated_at",
        ])

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class WorkOrderSub(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    work_order = models.ForeignKey(WorkOrderMain, on_delete=models.CASCADE, related_name="sub_items")

    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")
    suppliername = models.CharField(max_length=255, blank=True, default="")
    site_id = models.UUIDField(null=True, blank=True)
    workorderno = models.CharField(max_length=50, blank=True, default="")
    entry_date = models.DateField(null=True, blank=True)
    work_type = models.CharField(max_length=150, blank=True, default="")

    description_one = models.TextField(blank=True, default="")
    itemname = models.CharField(max_length=255, blank=True, default="")
    qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    unit_id = models.CharField(max_length=50, blank=True, default="")
    rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_per = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tot_tax_amnt = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    plant_name = models.CharField(max_length=150, blank=True, default="")
    staff_id = models.CharField(max_length=40, blank=True, default="")
    budget_no = models.CharField(max_length=50, blank=True, default="")
    type = models.CharField(max_length=50, blank=True, default="")
    wo_vp_app_qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        indexes = [models.Index(fields=["workorderno"])]

    def save(self, *args, **kwargs):
        self.amount = self.qty * self.rate
        self.tot_tax_amnt = (self.amount / 100) * self.tax_per if self.tax_per else 0
        super().save(*args, **kwargs)


class WorkOrderStatusFeed(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    work_order = models.ForeignKey(WorkOrderMain, on_delete=models.CASCADE, related_name="status_feeds")

    workorder_no = models.CharField(max_length=50, blank=True, default="")
    work_order_random_no = models.CharField(max_length=5, blank=True, default="")
    work_order_random_sc = models.CharField(max_length=12, blank=True, default="")
    entry_date = models.DateField(null=True, blank=True)
    site_id = models.UUIDField(null=True, blank=True)

    work_feed_status = models.CharField(max_length=50, blank=True, default="")
    work_feed_status_desc = models.TextField(blank=True, default="")
    paid_amt = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=50, blank=True, default="")
    department_name = models.CharField(max_length=150, blank=True, default="")

    work_order_dtc_pay_appr_status = models.CharField(max_length=5, default="0")
    work_order_dtc_pay_appr_date = models.DateTimeField(null=True, blank=True)
    work_order_dtc_pay_appr_desc = models.TextField(blank=True, default="")
    wo_ptm_dt_app_id = models.CharField(max_length=40, blank=True, default="")

    work_order_gm_pay_appr_status = models.CharField(max_length=5, default="0")
    work_order_gm_pay_appr_date = models.DateTimeField(null=True, blank=True)
    work_order_gm_pay_appr_desc = models.TextField(blank=True, default="")
    wo_ptm_gm_app_id = models.CharField(max_length=40, blank=True, default="")

    work_order_dt_pay_appr_status = models.CharField(max_length=5, default="0")
    work_order_dt_pay_appr_date = models.DateTimeField(null=True, blank=True)
    work_order_dt_pay_appr_desc = models.TextField(blank=True, default="")
    wo_ptm_dir_app_id = models.CharField(max_length=40, blank=True, default="")

    wo_supplier_pay_list_status = models.CharField(max_length=5, default="0")
    wo_supplier_pay_date = models.DateTimeField(null=True, blank=True)
    wo_supplier_pay_desc = models.TextField(blank=True, default="")
    wo_supplier_pay_type = models.CharField(max_length=50, blank=True, default="")
    wo_spp_ptm_lst_id = models.CharField(max_length=40, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["workorder_no"])]
