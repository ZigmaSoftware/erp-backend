from django.db import models

from shared.base_models import BaseMaster

from apps.sales_master.models.item_type_master import ItemTypeMaster
from apps.sales_master.models.sub_category_master import SubCategoryMaster
from apps.sales_master.models.target_entry_master import TargetEntryMaster


class TargetEntryItem(BaseMaster):

    target_entry = models.ForeignKey(
        TargetEntryMaster,
        on_delete=models.CASCADE,
        related_name="items",
        to_field="unique_id",
        db_column="target_entry_id",
    )

    item_type = models.ForeignKey(
        ItemTypeMaster,
        on_delete=models.PROTECT,
        related_name="target_entry_items",
        to_field="unique_id",
        db_column="item_type_id",
    )

    sub_category = models.ForeignKey(
        SubCategoryMaster,
        on_delete=models.PROTECT,
        related_name="target_entry_items",
        to_field="unique_id",
        db_column="sub_category_id",
        null=True,
        blank=True,
    )

    target_qty = models.DecimalField(max_digits=15, decimal_places=2)
    expense_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    revenue_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Mirrors the parent TargetEntryMaster's random_no/random_sc (shared
    # across all items of the same target entry, not unique per item).
    random_no = models.CharField(max_length=5, blank=True)
    random_sc = models.CharField(max_length=12, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.target_entry.target_no} - {self.item_type.item_type}"

    def save(self, *args, **kwargs):
        if self.target_entry_id:
            self.random_no = self.target_entry.random_no
            self.random_sc = self.target_entry.random_sc
        super().save(*args, **kwargs)
        if self.target_entry_id:
            self.target_entry.recalculate_totals()

    def delete(self, *args, **kwargs):
        """
        Soft delete (also refreshes the parent's totals)
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
