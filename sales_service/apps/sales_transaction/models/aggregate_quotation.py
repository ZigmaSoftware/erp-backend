import uuid
from django.db import models


class AggregateQuotationMain(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")
    quote_entry_no = models.CharField(max_length=50, unique=True)

    party_name = models.CharField(max_length=255)
    party_mobile_no = models.CharField(max_length=20)
    party_address = models.TextField(blank=True, default="")
    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    quote_month = models.CharField(max_length=20, help_text="e.g. January 2026")
    main_description = models.TextField(blank=True, default="")
    # Legacy `quote_file`: comma-separated stored filenames of uploaded quote docs.
    quote_file = models.TextField(blank=True, default="")

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
            models.Index(fields=["quote_month"]),
        ]

    def __str__(self):
        return self.quote_entry_no

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class AggregateQuotationSub(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    main = models.ForeignKey(AggregateQuotationMain, on_delete=models.CASCADE, related_name="sub_items")

    item_id = models.UUIDField(help_text="ItemCreation unique_id")
    material_type = models.CharField(max_length=50, blank=True, default="Others")
    item_name = models.CharField(max_length=255, blank=True, default="")
    unit_id = models.CharField(max_length=50, blank=True, default="")
    rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.item_name} - {self.rate}"
