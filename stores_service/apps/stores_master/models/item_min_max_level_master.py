from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster

from apps.stores_master.models.item_min_max_type_master import ItemMinMaxTypeMaster


class ItemMinMaxLevelMaster(BaseMaster):

    type = models.ForeignKey(
        ItemMinMaxTypeMaster,
        on_delete=models.PROTECT,
        related_name="min_max_levels",
        to_field="unique_id",
        db_column="type_id",
    )

    # Sales Service ItemCreation `unique_id` (no DB-level FK - cross-service reference).
    item_id = models.UUIDField()

    min_qty = models.DecimalField(max_digits=10, decimal_places=3)
    max_qty = models.DecimalField(max_digits=10, decimal_places=3)
    reorder = models.DecimalField(max_digits=10, decimal_places=3)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["type", "item_id"],
                condition=Q(is_deleted=False),
                name="uq_item_min_max_level_active",
            ),
        ]

    def __str__(self):
        return f"{self.type.type_name} - {self.item_id}"

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
