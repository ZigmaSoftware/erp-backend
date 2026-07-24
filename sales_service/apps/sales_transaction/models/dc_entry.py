import uuid
from django.db import models


class DcEntryForm(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")

    invoice_no = models.CharField(max_length=50, unique=True)
    ref_dc_no = models.CharField(max_length=50, blank=True, default="")
    entry_date = models.DateField()

    customer_name = models.UUIDField(help_text="CustomerCreationMaster unique_id")
    item_name = models.UUIDField(help_text="ItemCreation unique_id")
    qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)

    transport_name = models.CharField(max_length=255, blank=True, default="")
    transport_medium = models.CharField(max_length=150, blank=True, default="")
    destination = models.CharField(max_length=255, blank=True, default="")
    vehicle_no = models.CharField(max_length=50, blank=True, default="")

    load_weight = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    empty_weight = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    act_weight = models.DecimalField(max_digits=15, decimal_places=3, default=0)

    entry_time = models.TimeField(null=True, blank=True)
    exit_time = models.TimeField(null=True, blank=True)
    driver_name = models.CharField(max_length=150, blank=True, default="")
    driver_contact_no = models.CharField(max_length=20, blank=True, default="")
    description = models.TextField(blank=True, default="")

    site_id = models.UUIDField(help_text="Master Service Site unique_id")
    plant_name = models.CharField(max_length=150, blank=True, default="")
    state_id = models.UUIDField(null=True, blank=True)
    incharge_name = models.CharField(max_length=150, blank=True, default="")
    shift_name = models.CharField(max_length=50, blank=True, default="")

    work_order_no = models.CharField(max_length=50, blank=True, default="")
    freight_creation_id = models.UUIDField(null=True, blank=True)

    outward_ticket_no = models.CharField(max_length=50, blank=True, default="")
    outward_insert_id = models.UUIDField(null=True, blank=True)
    disposal_type = models.CharField(max_length=100, blank=True, default="")

    status = models.CharField(max_length=5, default="0")
    dc_no_status = models.CharField(max_length=5, default="0")
    coordinate_status = models.CharField(max_length=5, default="0")
    approve_date = models.DateTimeField(null=True, blank=True)
    approve_user = models.CharField(max_length=40, blank=True, default="")
    app_desc = models.TextField(blank=True, default="")

    dc_pdf = models.CharField(max_length=255, blank=True, default="")
    source_weigh_pdf = models.CharField(max_length=255, blank=True, default="")

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
            models.Index(fields=["site_id"]),
            models.Index(fields=["customer_name"]),
            models.Index(fields=["entry_date"]),
            models.Index(fields=["work_order_no"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.invoice_no

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
