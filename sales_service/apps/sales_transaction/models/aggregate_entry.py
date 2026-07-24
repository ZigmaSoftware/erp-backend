import uuid

from django.db import models


class AggregateEntryMain(models.Model):
    """
    Legacy: scrap_entry / scrap_entry_sub ("Aggregate Entry").
    Document number stored in `scrap_no`: SEN-{YYMM}-NNNN (calendar-year reset).
    """

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=40, blank=True, default="")
    scrap_no = models.CharField(max_length=50, unique=True, help_text="Legacy SEN-{YYMM}-NNNN number")

    entry_date = models.DateField()
    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    plant_id = models.UUIDField(null=True, blank=True, help_text="Plant master unique_id")
    plant_name = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["scrap_no"]),
            models.Index(fields=["site_id"]),
            models.Index(fields=["entry_date"]),
        ]

    def __str__(self):
        return self.scrap_no

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class AggregateEntrySub(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    main = models.ForeignKey(AggregateEntryMain, on_delete=models.CASCADE, related_name="sub_items")

    item_id = models.UUIDField(null=True, blank=True, help_text="ItemCreation unique_id")
    item_name = models.CharField(max_length=255, blank=True, default="")
    # In legacy PHP `stock` is auto-fetched from MBS percentage data
    # (mbs_percent_sublist), owned by another module and not present in
    # sales_service; accepted as input here until an MBS read-model exists.
    stock = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    receipt = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    remarks = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.item_name} - {self.stock}"
