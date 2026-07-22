from django.db import models

from shared.base_models import BaseMaster

from apps.sales_master.models.item_type_master import ItemTypeMaster
from apps.sales_master.models.scrap_sales_category_master import ScrapSalesCategoryMaster


class ItemCreation(BaseMaster):

    item_type_id = models.ForeignKey(
        ItemTypeMaster,
        on_delete=models.PROTECT,
        related_name="items",
        to_field="unique_id",
        db_column="item_type_id",
    )

    category_id = models.ForeignKey(
        ScrapSalesCategoryMaster,
        on_delete=models.PROTECT,
        related_name="items",
        to_field="unique_id",
        db_column="category_id",
    )

    # Master Service Site `unique_id` (no DB-level FK - see SALES_SERVICE_README.md).
    site_id = models.UUIDField()

    item_name = models.CharField(max_length=150)
    purpose_application = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def item_code(self):
        return str(self.id)

    def __str__(self):
        return f"{self.item_code} - {self.item_name}"

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
