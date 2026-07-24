import uuid
from django.db import models


class AfrTransportRfq(models.Model):

    class EmailMode(models.IntegerChoices):
        # Legacy afr_logistics_rfq/create.php: 0 = Individual, 1 = All transporters.
        INDIVIDUAL = 0, "Individual"
        ALL = 1, "All Transporters"

    class LoadType(models.TextChoices):
        # Legacy afr_logistics_rfq/create.php stores "Ton" / "Load".
        TON = "Ton", "Ton"
        LOAD = "Load", "Load"

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    request_quotation_transportation = models.CharField(max_length=50, help_text="e.g. RDF, MSW")
    source = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    load_type = models.CharField(max_length=20, choices=LoadType.choices, default=LoadType.TON)
    due_date = models.DateField()
    site_id = models.UUIDField(null=True, blank=True, help_text="Master Service Site unique_id")

    email_mode = models.IntegerField(choices=EmailMode.choices, default=EmailMode.ALL)
    toemail = models.TextField(blank=True, default="", help_text="Comma-separated email IDs")
    bcc = models.TextField(blank=True, default="")

    status = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["due_date"]),
            models.Index(fields=["site_id"]),
        ]

    def __str__(self):
        return f"RFQ-{self.request_quotation_transportation}-{self.unique_id}"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
