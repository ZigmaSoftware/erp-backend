from django.db import models

from shared.base_models import BaseMaster

from apps.sales_master.models.customer_creation_master import CustomerCreationMaster


class CustomerDestination(BaseMaster):

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    customer = models.ForeignKey(
        CustomerCreationMaster,
        on_delete=models.CASCADE,
        related_name="destinations",
        to_field="unique_id",
        db_column="customer_id",
    )

    # Master Service Site `unique_id` (no DB-level FK - see SALES_SERVICE_README.md).
    site = models.UUIDField()

    destination = models.CharField(max_length=150)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.customer_name} - {self.destination}"

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
