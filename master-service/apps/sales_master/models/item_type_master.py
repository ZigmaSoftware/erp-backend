from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class ItemTypeMaster(BaseMaster):

    item_type = models.CharField(max_length=150)

    class Meta:
        ordering = ["item_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["item_type"],
                condition=Q(is_deleted=False),
                name="uq_item_type_name_active"
            ),
        ]

    def __str__(self):
        return self.item_type

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
