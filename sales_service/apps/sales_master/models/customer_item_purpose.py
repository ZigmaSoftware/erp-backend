from django.db import models

from shared.base_models import BaseMaster

from apps.sales_master.models.customer_creation_master import CustomerCreationMaster
from apps.sales_master.models.item_creation import ItemCreation


class CustomerItemPurpose(BaseMaster):

    class DisposalType(models.TextChoices):
        CUSTOMER_SCOPE = "customer_scope", "Customer Scope"
        ZIGMA_SCOPE = "zigma_scope", "Zigma Scope"
        TRANSPORT_SCOPE = "transport_scope", "Transport Scope"

    class PurposeApplication(models.TextChoices):
        LAND_FILL_EARTH_FILL = "land_fill_earth_fill", "Land Fill / Earth Fill"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    customer = models.ForeignKey(
        CustomerCreationMaster,
        on_delete=models.CASCADE,
        related_name="item_purposes",
        to_field="unique_id",
        db_column="customer_id",
    )

    # Master Service Site `unique_id` (no DB-level FK - see SALES_SERVICE_README.md).
    site = models.UUIDField()

    destination = models.CharField(max_length=150)

    item = models.ForeignKey(
        ItemCreation,
        on_delete=models.PROTECT,
        related_name="customer_item_purposes",
        to_field="unique_id",
        db_column="item_id",
    )

    disposal_type = models.CharField(max_length=20, choices=DisposalType.choices)
    purpose_application = models.CharField(
        max_length=30, choices=PurposeApplication.choices
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.customer_name} - {self.item.item_name}"

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
