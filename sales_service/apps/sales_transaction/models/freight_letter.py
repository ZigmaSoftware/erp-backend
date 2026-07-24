import uuid
from django.db import models


class FreightLetter(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    dc_entry_id = models.UUIDField(help_text="DcEntryForm unique_id")
    freight_entry_id = models.UUIDField(help_text="FreightCreation unique_id")
    letter_no = models.CharField(max_length=50, unique=True)
    entry_date = models.DateField()
    customer_name = models.UUIDField(help_text="CustomerCreationMaster unique_id")
    site_id = models.UUIDField(help_text="Master Service Site unique_id")

    transport_name = models.CharField(max_length=255, blank=True, default="")
    driver_name = models.CharField(max_length=150, blank=True, default="")
    driver_contact_no = models.CharField(max_length=20, blank=True, default="")
    vehicle_no = models.CharField(max_length=20, blank=True, default="")
    document_file = models.FileField(upload_to="freight_letters/%Y/%m/", blank=True, null=True)

    status = models.CharField(max_length=20, default="active")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["letter_no"]),
            models.Index(fields=["site_id"]),
            models.Index(fields=["entry_date"]),
        ]

    def __str__(self):
        return self.letter_no
