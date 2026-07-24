import uuid
from django.db import models


class FreightCreation(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=12, blank=True, default="")

    date = models.DateField()
    source = models.UUIDField(help_text="Source Site unique_id")
    destination = models.CharField(max_length=255, blank=True, default="")
    freight_no = models.CharField(max_length=50, unique=True)

    vehicle_no = models.CharField(max_length=50, blank=True, default="")
    material = models.CharField(max_length=255, blank=True, default="")
    vehicle_type = models.CharField(max_length=150, blank=True, default="")
    driver_name = models.CharField(max_length=150, blank=True, default="")
    mobile_no = models.CharField(max_length=20, blank=True, default="")
    date_of_transfer = models.DateField(null=True, blank=True)

    freight_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    advance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    account_no = models.CharField(max_length=50, blank=True, default="")
    bank_name = models.CharField(max_length=150, blank=True, default="")
    branch_address = models.CharField(max_length=255, blank=True, default="")
    ifsc_code = models.CharField(max_length=20, blank=True, default="")

    transport_name = models.CharField(max_length=255, blank=True, default="")
    transport_address = models.CharField(max_length=255, blank=True, default="")
    transport_contact_no = models.CharField(max_length=20, blank=True, default="")
    payment_mode = models.CharField(max_length=50, blank=True, default="")

    customer_id = models.UUIDField(null=True, blank=True)
    dc_no = models.CharField(max_length=50, blank=True, default="")

    freight_status = models.CharField(max_length=5, default="0")
    freight_approve_date = models.DateTimeField(null=True, blank=True)
    coordinate_status = models.CharField(max_length=5, default="0")
    approve_date = models.DateTimeField(null=True, blank=True)
    approve_user = models.CharField(max_length=40, blank=True, default="")
    app_desc = models.TextField(blank=True, default="")
    payable_status = models.CharField(max_length=5, default="0")

    add_user = models.CharField(max_length=40, blank=True, default="")
    edit_user = models.CharField(max_length=40, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["freight_no"]),
            models.Index(fields=["source"]),
            models.Index(fields=["date"]),
            models.Index(fields=["coordinate_status"]),
        ]

    def __str__(self):
        return self.freight_no

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
