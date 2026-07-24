import uuid
from django.db import models


class AggregateComparison(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    quote_entry_no = models.CharField(max_length=50, unique=True)
    quote_month = models.CharField(max_length=20)
    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    comp_description = models.TextField(blank=True, default="")

    status = models.CharField(max_length=10, default="Pending")
    status_by = models.CharField(max_length=40, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["quote_entry_no"]),
            models.Index(fields=["site_id"]),
        ]

    def __str__(self):
        return self.quote_entry_no

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class AggregateComparisonSub(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    comparison = models.ForeignKey(AggregateComparison, on_delete=models.CASCADE, related_name="sub_items")

    quote_entry_no = models.CharField(max_length=50)
    material_id = models.UUIDField(null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    quote_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    quote_check_list = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]



