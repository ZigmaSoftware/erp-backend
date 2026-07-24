import uuid
from django.db import models


class DailyTargetDisposalMain(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")
    entry_no = models.CharField(max_length=50, unique=True)

    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    entry_date = models.DateField()

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["entry_no"]),
            models.Index(fields=["site_id"]),
            models.Index(fields=["entry_date"]),
        ]

    def __str__(self):
        return self.entry_no

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class DailyTargetDisposalSub(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    main = models.ForeignKey(DailyTargetDisposalMain, on_delete=models.CASCADE, related_name="sub_items")

    dte_customer_name = models.UUIDField(help_text="CustomerCreationMaster unique_id")
    dte_customer_order = models.CharField(max_length=150, blank=True, default="")
    dte_item_name = models.CharField(max_length=255, blank=True, default="")
    dte_item_type = models.CharField(max_length=150, blank=True, default="")
    dte_item_id = models.UUIDField(null=True, blank=True)
    dte_customer_order_qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    dte_order_qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    dte_trans_name = models.UUIDField(null=True, blank=True, help_text="TransportEntryMaster unique_id")
    dte_trans_order_no = models.CharField(max_length=50, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.dte_item_name} - {self.dte_order_qty}"
