from django.db import models
from django.db.models import Q

from apps.sales_master.models.item_type_master import ItemTypeMaster
from shared.base_models import BaseMaster


class ItemGroupCreationMaster(BaseMaster):

    item_type = models.ForeignKey(
        ItemTypeMaster,
        on_delete=models.PROTECT,
        related_name="item_groups",
        to_field="unique_id",
        db_column="item_type_id",
    )
    sub_category_name = models.CharField(max_length=150)
    item_name = models.TextField()
    item_id = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        ordering = ["sub_category_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["item_type", "sub_category_name"],
                condition=Q(is_deleted=False),
                name="uq_item_group_sub_category_active",
            ),
        ]

    def __str__(self):
        return self.sub_category_name

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
